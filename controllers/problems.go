package controllers

import (
	"log"
	"net/http"
	"time"

	"github.com/pranav244872/dsa-recall/context"
	"github.com/pranav244872/dsa-recall/models"
)

///////////////////////////////////////////////////////////////////////////////
// Problems Controller
///////////////////////////////////////////////////////////////////////////////

// Problems controller struct to handle problem-related routes
type Problems struct {
	ProblemService *models.ProblemService
}

// Constructor for Problems controller
func NewProblems(ps *models.ProblemService) *Problems {
	return &Problems{
		ProblemService: ps,
	}
}

///////////////////////////////////////////////////////////////////////////////
// Create Problem
///////////////////////////////////////////////////////////////////////////////

type CreateProblemForm struct {
	Title    string `json:"title"`
	Link     string `json:"link"`
	Approach string `json:"approach"`
	Code     string `json:"code"`
}

// Create handles the problem creation process
// it is a protected endpoint only logged in users can access
// It expects a JSON payload and returns a JSON response
func (p *Problems) Create(w http.ResponseWriter, r *http.Request) {
	var form CreateProblemForm
	if err := parseJSON(r, &form); err != nil {
		respondWithError(w, http.StatusBadRequest, "Invalid JSON payload")
		return
	}

	// get user from context
	user := context.User(r.Context())
	if user == nil {
		respondWithError(w, http.StatusInternalServerError, "Unable to find user from context")
		return
	}

	// Set initial spaced repetition data
	problem := models.Problem{
		UserID:         user.ID,
		Title:          form.Title,
		Link:           form.Link,
		Approach:       form.Approach,
		Code:           form.Code,
		CurrentStreak:  0,                           // A new problem starts with a streak of 0
		NextReviewDate: time.Now().AddDate(0, 0, 1), // Due for review tomorrow
	}

	if err := p.ProblemService.DB.Create(&problem); err != nil {
		log.Println("problem controller: Error creating problem:", err)
		respondWithError(w, http.StatusInternalServerError, "Something went wrong. Please try again")
		return
	}

	respondWithJSON(w, http.StatusCreated, problem)
}
