package main

import (
	"context"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
	"github.com/pranav244872/dsa-recall/config"
	"github.com/pranav244872/dsa-recall/controllers"
	"github.com/pranav244872/dsa-recall/models"
)

type Server struct {
	router      *chi.Mux
	userService *models.UserService
}

// NewServer creates a new server with all the routes and dependencies
func NewServer(userService *models.UserService) *Server {
	s := &Server{
		router:      chi.NewRouter(),
		userService: userService,
	}

	// Regester middleware and routes
	s.configureRouter()

	return s
}

// configureRouter sets up middleware and registers all the application routes
func (s *Server) configureRouter() {
	// A good base middleware stack
	s.router.Use(middleware.RequestID)
	s.router.Use(middleware.RealIP)
	s.router.Use(middleware.Logger)
	s.router.Use(middleware.Recoverer)

	// Set a timeout value on the request context
	s.router.Use(middleware.Timeout(60 * time.Second))

	// CORS configuration
	s.router.Use(corsConfig())

	// User routes
	usersC := controllers.NewUsers(s.userService)
	s.router.Post("/api/signup", usersC.Create)
	s.router.Post("/api/login", usersC.Login)
	s.router.Post("/api/logout", usersC.Logout)
	s.router.Get("/api/me", usersC.CurrentUser)
}

// ServeHTTP makes our Server implemment the http.Handler interface
func (s *Server) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	s.router.ServeHTTP(w, r)
}

func main() {
	// Load environment variables from .env
	config.LoadEnv()

	// Connect to database
	dsn := config.GetDSN()
	userService, err := models.NewUserService(dsn)

	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}

	defer func() {
		log.Println("Closing database connection....")
		if err := userService.DB.Close(); err != nil {
			log.Printf("Error closing DB: %v", err)
		}
	}()

	log.Println("Database connected")
	// Auto-migrate schema
	if err := userService.DB.DestructiveReset(); err != nil {
		log.Fatalf("Failed to migrate database: %v", err)
	}

	// Create our server
	server := NewServer(userService)

	// Graceful shutdown setup
	addr := config.ServerHost + ":" + config.ServerPort
	httpServer := &http.Server{
		Addr:    addr,
		Handler: server,
	}

	go func() {
		log.Println("Server starting on https://" + addr)
		if err := httpServer.ListenAndServeTLS(config.CertFile, config.KeyFile); err != nil && err != http.ErrServerClosed {
			log.Fatalf("Could not start HTTPS server: %v", err)
		}
	}()

	// Listen for Ctrl + C or SIGTERM
	waitForShutdown(httpServer)
}

func waitForShutdown(server *http.Server) {
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, os.Interrupt, syscall.SIGTERM)
	<-quit
	log.Println("Shutting down server gracefully....")

	// Create a context with a timeout to allow existing connections to finish
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	if err := server.Shutdown(ctx); err != nil {
		log.Fatalf("Server shutdown failed: %v", err)
	}

	log.Println("Server exited properly")
}

func corsConfig() func(http.Handler) http.Handler {
	// A simple CORS middleware
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.Header().Set("Access-Control-Allow-Origin", config.ClientOrigin)
			w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
			w.Header().Set("Access-Control-Allow-Headers", "Accept, Authorization, Content-Type, X-CSRF-Token")
			w.Header().Set("Access-Control-Allow-Credentials", "true")

			if r.Method == "OPTIONS" {
				w.WriteHeader(http.StatusOK)
				return
			}

			next.ServeHTTP(w, r)
		})
	}
}
