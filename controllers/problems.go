package controllers

import (
	"log"
	"math"
	"net/http"
	"strconv"
	"time"

	"github.com/go-chi/chi/v5"
	"github.com/pranav244872/dsa-recall/context"
	"github.com/pranav244872/dsa-recall/models"
)

///////////////////////////////////////////////////////////////////////////////
// Problems Controller
///////////////////////////////////////////////////////////////////////////////

// Problems controller struct to handle problem-related routes
type Problems struct {
	ProblemService  *models.ProblemService
	UserService     *models.UserService
	ActivityService *models.ActivityService
}

// Constructor for Problems controller
func NewProblems(ps *models.ProblemService, us *models.UserService, as *models.ActivityService) *Problems {
	return &Problems{
		ProblemService:  ps,
		UserService:     us,
		ActivityService: as,
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
	Language string `json:"language"`
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
		Language:       form.Language,
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

///////////////////////////////////////////////////////////////////////////////
// Get Problem
///////////////////////////////////////////////////////////////////////////////

// Show handles the problem retrieval
// it is a protected endpoint only logged in users can access
// It expects a JSON payload and returns a JSON response
func (p *Problems) Show(w http.ResponseWriter, r *http.Request) {
	// Get the problem ID from the route
	idStr := chi.URLParam(r, "problemID")

	// Convert string to uint
	idUint64, err := strconv.ParseUint(idStr, 10, 64)
	if err != nil {
		respondWithError(w, http.StatusBadRequest, "Invalid problem ID")
		return
	}
	id := uint(idUint64)

	// Get the user from the context
	user := context.User(r.Context())
	if user == nil {
		respondWithError(w, http.StatusInternalServerError, "Unable to retrieve user from context")
		return
	}

	// Look up the problem
	problem, err := p.ProblemService.DB.ByID(id)
	if err != nil {
		if err == models.ErrorNotFound {
			respondWithError(w, http.StatusNotFound, "Problem not found")
			return
		}
		respondWithError(w, http.StatusInternalServerError, "Database error")
		return
	}

	// Check if the problem belongs to the current user
	if problem.UserID != user.ID {
		respondWithError(w, http.StatusNotFound, "Problem not found") // pretend it doesn't exist
		return
	}

	// Return the problem
	respondWithJSON(w, http.StatusOK, problem)
}

///////////////////////////////////////////////////////////////////////////////
// Get All Problems of a user
///////////////////////////////////////////////////////////////////////////////

// List handles the problems retrieval for a particular user
// it is a protected endpoint only logged in users can access
// It expects a JSON payload and returns a JSON response
func (p *Problems) List(w http.ResponseWriter, r *http.Request) {
	// Get the user from the context
	user := context.User(r.Context())
	if user == nil {
		respondWithError(w, http.StatusInternalServerError, "Unable to find user from context")
		return
	}

	// Parse query parameters with defaults
	page, _ := strconv.Atoi(r.URL.Query().Get("page"))
	if page < 1 {
		page = 1
	}
	limit, _ := strconv.Atoi(r.URL.Query().Get("limit"))
	if limit < 1 {
		limit = 10
	}
	searchTerm := r.URL.Query().Get("q")

	// Fetch all problems for the user
	paginatedResult, err := p.ProblemService.DB.ByUserID(user.ID, searchTerm, page, limit)
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, "Failed to fetch problems")
		return
	}

	response := map[string]any{
		"problems": paginatedResult.Problems,
		"meta": map[string]any{
			"total_records": paginatedResult.Total,
			"current_page":  page,
			"page_size":     limit,
			"total_pages":   int(math.Ceil(float64(paginatedResult.Total) / float64(limit))),
		},
	}
	// Return the problems as JSON
	respondWithJSON(w, http.StatusOK, response)
}

///////////////////////////////////////////////////////////////////////////////
// Get All Due Problems of a user
///////////////////////////////////////////////////////////////////////////////

// ListDue handles retrieving all problems due for review for a user.
func (p *Problems) ListDue(w http.ResponseWriter, r *http.Request) {
	user := context.User(r.Context())
	if user == nil {
		respondWithError(w, http.StatusInternalServerError, "Unable to find user from context")
		return
	}

	// Parse page and limit from query parameters, with defaults
	page, _ := strconv.Atoi(r.URL.Query().Get("page"))
	if page < 1 {
		page = 1
	}
	limit, _ := strconv.Atoi(r.URL.Query().Get("limit"))
	if limit < 1 {
		limit = 10
	}

	// Fetch paginated results for due problems
	paginatedResult, err := p.ProblemService.DB.ByUserIDAndDue(user.ID, page, limit)
	if err != nil {
		log.Println("problem controller: Error fetching due problems:", err)
		respondWithError(w, http.StatusInternalServerError, "Failed to fetch due problems")
		return
	}

	response := map[string]any{
		"problems": paginatedResult.Problems,
		"meta": map[string]any{
			"total_records": paginatedResult.Total,
			"current_page":  page,
			"page_size":     limit,
			"total_pages":   int(math.Ceil(float64(paginatedResult.Total) / float64(limit))),
		},
	}

	respondWithJSON(w, http.StatusOK, response)
}

///////////////////////////////////////////////////////////////////////////////
// Update Problem
///////////////////////////////////////////////////////////////////////////////

type UpdateProblemForm struct {
	Title    *string `json:"title"`
	Link     *string `json:"link"`
	Approach *string `json:"approach"`
	Code     *string `json:"code"`
	Language *string `json:"language"`
}

// Update handles the problem updation
// it is a protected endpoint only logged in users can access
// It expects a JSON payload and returns a JSON response
func (p *Problems) Update(w http.ResponseWriter, r *http.Request) {
	// Get the problem ID from the route
	idStr := chi.URLParam(r, "problemID")

	// Convert string to uint
	idUint64, err := strconv.ParseUint(idStr, 10, 64)
	if err != nil {
		respondWithError(w, http.StatusBadRequest, "Invalid problem ID")
		return
	}
	id := uint(idUint64)

	// Get the user from the context
	user := context.User(r.Context())
	if user == nil {
		respondWithError(w, http.StatusInternalServerError, "Unable to retrieve user from context")
		return
	}

	// Look up the existing problem
	problem, err := p.ProblemService.DB.ByID(id)
	if err != nil {
		if err == models.ErrorNotFound {
			respondWithError(w, http.StatusNotFound, "Problem not found")
			return
		}
		respondWithError(w, http.StatusInternalServerError, "Database error")
		return
	}

	// Check if the problem belongs to the current user
	if problem.UserID != user.ID {
		respondWithError(w, http.StatusNotFound, "Problem not found")
		return
	}

	// Decode JSON body into UpdateProblemForm
	var form UpdateProblemForm
	if err := parseJSON(r, &form); err != nil {
		respondWithError(w, http.StatusBadRequest, "Invalid JSON payload")
		return
	}

	// Apply updates only for fields provided
	if form.Title != nil {
		problem.Title = *form.Title
	}
	if form.Link != nil {
		problem.Link = *form.Link
	}
	if form.Approach != nil {
		problem.Approach = *form.Approach
	}
	if form.Code != nil {
		problem.Code = *form.Code
	}
	if form.Language != nil {
		problem.Language = *form.Language
	}

	// Save updated problem (validation happens inside Update)
	if err := p.ProblemService.DB.Update(problem); err != nil {
		log.Println("problem controller: Error updating problem:", err)
		respondWithError(w, http.StatusInternalServerError, "Something went wrong updating the problem")
		return
	}

	// Respond with updated problem JSON
	respondWithJSON(w, http.StatusOK, problem)
}

// /////////////////////////////////////////////////////////////////////////////
// Review Problem
// /////////////////////////////////////////////////////////////////////////////

type ReviewProblemForm struct {
	IsEasy bool `json:"is_easy"`
}

// Review handles updating a problem's spaced repetition data.
func (p *Problems) Review(w http.ResponseWriter, r *http.Request) {
	// Get ID and verify ownership
	idStr := chi.URLParam(r, "problemID")
	idUint64, err := strconv.ParseUint(idStr, 10, 64)
	if err != nil {
		respondWithError(w, http.StatusBadRequest, "Invalid problem ID")
		return
	}
	id := uint(idUint64)

	user := context.User(r.Context())
	problem, err := p.ProblemService.DB.ByID(id)
	if err != nil {
		respondWithError(w, http.StatusNotFound, "Problem not found")
		return
	}
	if problem.UserID != user.ID {
		respondWithError(w, http.StatusNotFound, "Problem not found")
		return
	}

	// Parse request body
	var form ReviewProblemForm
	if err := parseJSON(r, &form); err != nil {
		respondWithError(w, http.StatusBadRequest, "Invalid JSON payload")
		return
	}

	// Update User Streak and Last Practiced At
	now := time.Now()
	today := time.Date(now.Year(), now.Month(), now.Day(), 0, 0, 0, 0, now.Location())

	if user.LastPracticedAt == nil {
		user.CurrentStreak = 1 // First practice
	} else {
		lastPracticeDay := time.Date(user.LastPracticedAt.Year(), user.LastPracticedAt.Month(), user.LastPracticedAt.Day(), 0, 0, 0, 0, user.LastPracticedAt.Location())
		yesterday := today.AddDate(0, 0, -1)

		if lastPracticeDay.Before(yesterday) {
			user.CurrentStreak = 1 // Streak broken
		} else if lastPracticeDay.Equal(yesterday) {
			user.CurrentStreak++ // Consecutive day
		}
		// If lastPracticeDay is today, streak does not change.
	}
	user.LastPracticedAt = &now

	if err := p.UserService.DB.Update(user); err != nil {
		log.Println("problem controller: Error updating user streak:", err)
		respondWithError(w, http.StatusInternalServerError, "Failed to update user streak")
		return
	}

	// Log the activity
	activity := models.Activity{
		UserID:     user.ID,
		ProblemID:  problem.ID,
		ReviewedAt: now,
	}
	if err := p.ActivityService.DB.Create(&activity); err != nil {
		log.Println("problem controller: Error creating activity log:", err)
	}

	// Apply the spaced repetition algorithm to the problem
	if form.IsEasy {
		problem.CurrentStreak++
		problem.NextReviewDate = time.Now().AddDate(0, 0, problem.CurrentStreak)
	} else {
		problem.CurrentStreak = 0
		problem.NextReviewDate = time.Now().AddDate(0, 0, 1)
	}

	if err := p.ProblemService.DB.Update(problem); err != nil {
		log.Println("problem controller: Error updating problem after review:", err)
		respondWithError(w, http.StatusInternalServerError, "Failed to update problem")
		return
	}

	respondWithJSON(w, http.StatusOK, problem)
}

///////////////////////////////////////////////////////////////////////////////
// Delete Problem
///////////////////////////////////////////////////////////////////////////////

// Delete handles the problem deletion
// it is a protected endpoint only logged in users can access
// It expects a JSON payload and returns a JSON response
func (p *Problems) Delete(w http.ResponseWriter, r *http.Request) {
	// Get the problem ID from the route
	idStr := chi.URLParam(r, "problemID")

	// Convert string to uint
	idUint64, err := strconv.ParseUint(idStr, 10, 64)
	if err != nil {
		respondWithError(w, http.StatusBadRequest, "Invalid problem ID")
		return
	}
	id := uint(idUint64)

	// Get the user from the context
	user := context.User(r.Context())
	if user == nil {
		respondWithError(w, http.StatusInternalServerError, "Unable to retrieve user from context")
		return
	}

	// Look up the problem to verify ownership
	problem, err := p.ProblemService.DB.ByID(id)
	if err != nil {
		if err == models.ErrorNotFound {
			respondWithError(w, http.StatusNotFound, "Problem not found")
			return
		}
		respondWithError(w, http.StatusInternalServerError, "Database error")
		return
	}

	// Check if the problem belongs to the current user
	if problem.UserID != user.ID {
		respondWithError(w, http.StatusNotFound, "Problem not found") // hide existence for unauthorized users
		return
	}

	// Delete the problem
	if err := p.ProblemService.DB.Delete(id); err != nil {
		log.Println("problem controller: Error deleting problem:", err)
		respondWithError(w, http.StatusInternalServerError, "Could not delete problem")
		return
	}

	// Respond with no content on success
	w.WriteHeader(http.StatusNoContent)
}
