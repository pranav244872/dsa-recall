package controllers

import (
	"encoding/json"
	"errors"
	"log"
	"net/http"
	"time"

	"github.com/pranav244872/dsa-recall/models"
	"github.com/pranav244872/dsa-recall/rand"
)

///////////////////////////////////////////////////////////////////////////////
// Users Controller
///////////////////////////////////////////////////////////////////////////////

// Users controller struct to handle user-related routes
type Users struct {
	UserService *models.UserService
}

// Constructor for Users controller
func NewUsers(us *models.UserService) *Users {
	return &Users{
		UserService: us,
	}
}

///////////////////////////////////////////////////////////////////////////////
// User Signup
///////////////////////////////////////////////////////////////////////////////

// SignupForm defines the expected JSON structure for a new user signup
type SignupForm struct {
	Name     string `json:"name"`
	Email    string `json:"email"`
	Password string `json:"password"`
}

// Create handles the user signup process and it automatically logs the user in
// It expects a JSON payload and returns a JSON response
func (u *Users) Create(w http.ResponseWriter, r *http.Request) {
	var form SignupForm
	if err := parseJSON(r, &form); err != nil {
		respondWithError(w, http.StatusBadRequest, "Invalid JSON payload")
		return
	}

	user := models.User{
		Name:     form.Name,
		Email:    form.Email,
		Password: form.Password,
	}

	if err := u.UserService.DB.Create(&user); err != nil {
		// Check for the specific error for a duplicate email.
		if errors.Is(err, models.ErrorEmailTaken) {
			respondWithError(w, http.StatusConflict, "That email address is already taken!")
			return
		}

		log.Println("user controller: Error creating user:", err)
		respondWithError(w, http.StatusInternalServerError, "Something went wrong. Please try again")
		return
	}

	// automatically sign the user in after they create an account
	if err := u.signIn(w, &user); err != nil {
		log.Println("user controller: Error signing in new user:", err)
		respondWithError(w, http.StatusInternalServerError, "Account created but failed to sign you in")
		return
	}

	responsePayload := map[string]string{"message": "User created and logged in successfully!"}
	respondWithJSON(w, http.StatusCreated, responsePayload)
}

///////////////////////////////////////////////////////////////////////////////
// User Login
///////////////////////////////////////////////////////////////////////////////

// LoginForm defines the expected JSON structure for user login
type LoginForm struct {
	Email    string `json:"email"`
	Password string `json:"password"`
}

// Login handles the user authentication process
func (u *Users) Login(w http.ResponseWriter, r *http.Request) {
	form := LoginForm{}
	if err := parseJSON(r, &form); err != nil {
		respondWithError(w, http.StatusBadRequest, "Invalid JSON payload")
		return
	}

	user, err := u.UserService.Authenticate(form.Email, form.Password)
	if err != nil {
		// 3. Relay the Result
		switch err {
		case models.ErrorNotFound, models.ErrorIncorrectPassword:
			respondWithError(w, http.StatusUnauthorized, "Invalid Credentials")
		default:
			log.Println("user controller: Error authenticating user:", err)
			respondWithError(w, http.StatusInternalServerError, "Something went wrong. Please try again")
		}
		return
	}

	if err := u.signIn(w, user); err != nil {
		log.Println("user controller: Error signing in user:", err)
		respondWithError(w, http.StatusInternalServerError, "Failed to sign in")
		return
	}

	// Respond with user data (or token, in a real app)
	respondWithJSON(w, http.StatusOK, map[string]string{"message": "Login successful"})
}

///////////////////////////////////////////////////////////////////////////////
// User Logout
///////////////////////////////////////////////////////////////////////////////

func (u *Users) Logout(w http.ResponseWriter, r *http.Request) {
	cookie := http.Cookie{
		Name:     "remember_token",
		Value:    "",
		Expires:  time.Now().Add(-time.Hour), // Set expiry to the past
		HttpOnly: true,
		Secure:   true,
		SameSite: http.SameSiteNoneMode,
	}
	http.SetCookie(w, &cookie)
	respondWithJSON(w, http.StatusOK, map[string]string{"message": "Logged out successfully"})
}

///////////////////////////////////////////////////////////////////////////////
// User Cookie Test
///////////////////////////////////////////////////////////////////////////////

type UserResponse struct {
	ID    int64  `json:"id"`
	Name  string `json:"name"`
	Email string `json:"email"`
}

// CurrentUser acts as a protected endpoint to verify a user's session.
func (u *Users) CurrentUser(w http.ResponseWriter, r *http.Request) {
	cookie, err := r.Cookie("remember_token")
	if err != nil {
		respondWithError(w, http.StatusUnauthorized, "Authentication required")
		return
	}

	user, err := u.UserService.DB.ByRememberToken(cookie.Value)
	if err != nil {
		respondWithError(w, http.StatusUnauthorized, "Invalid session token")
		return
	}

	response := UserResponse{
		ID:    user.ID,
		Name:  user.Name,
		Email: user.Email,
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

///////////////////////////////////////////////////////////////////////////////
// Helper functions
///////////////////////////////////////////////////////////////////////////////

// signIn helper function sign in users via cookies
func (u *Users) signIn(w http.ResponseWriter, user *models.User) error {
	// Generate a new remember token for every sign-in.
	token, err := rand.RememberToken()
	if err != nil {
		return err
	}
	user.Remember = token

	if err := u.UserService.DB.Update(user); err != nil {
		return err
	}

	cookie := http.Cookie{
		Name:     "remember_token",
		Value:    user.Remember,
		HttpOnly: true,
		Secure:   true,
		SameSite: http.SameSiteNoneMode,
	}

	http.SetCookie(w, &cookie)
	return nil
}
