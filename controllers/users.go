package controllers

import (
	"encoding/json"
	"errors"
	"net/http"

	"github.com/pranav244872/dsa-recall/models"
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
			respondWithError(w, http.StatusConflict, err.Error())
			return
		}

		respondWithError(w, http.StatusBadRequest, "Failed to create new user")
		return
	}

	// automatically sign the user in after they create an account
	if err := u.signIn(w, &user); err != nil {
		respondWithError(w, http.StatusInternalServerError, "Something went wrong during sign-in")
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
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}

	user, err := u.UserService.Authenticate(form.Email, form.Password)
	if err != nil {
		// 3. Relay the Result
		switch err {
		case models.ErrorNotFound, models.ErrorIncorrectPassword:
			http.Error(w, "Invalid credentials", http.StatusUnauthorized)
		default:
			http.Error(w, "Something went wrong", http.StatusInternalServerError)
		}
		return
	}

	if err := u.signIn(w, user); err != nil {
		respondWithError(w, http.StatusInternalServerError, "Failed to sign in")
		return
	}

	// Respond with user data (or token, in a real app)
	respondWithJSON(w, http.StatusOK, map[string]string{"message": "Login successful"})
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
		http.Error(w, "Authentication required", http.StatusUnauthorized)
		return
	}

	user, err := u.UserService.DB.ByRememberToken(cookie.Value)
	if err != nil {
		http.Error(w, "Invalid session token", http.StatusUnauthorized)
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
