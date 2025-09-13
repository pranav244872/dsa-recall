package controllers

import (
	"log"
	"net/http"
	"strconv"

	"github.com/pranav244872/dsa-recall/context"
	"github.com/pranav244872/dsa-recall/models"
)

///////////////////////////////////////////////////////////////////////////////
// Activities Controller
///////////////////////////////////////////////////////////////////////////////

type Activities struct {
	ActivityService *models.ActivityService
}

func NewActivities(as *models.ActivityService) *Activities {
	return &Activities{ActivityService: as}
}

///////////////////////////////////////////////////////////////////////////////
// Get Heatmap
///////////////////////////////////////////////////////////////////////////////

func (a *Activities) Heatmap(w http.ResponseWriter, r *http.Request) {
	user := context.User(r.Context())
	if user == nil {
		respondWithError(w, http.StatusUnauthorized, "User not found")
		return
	}

	// Get the 'months' query param, default to 6 if not provided
	monthsStr := r.URL.Query().Get("months")
	months, err := strconv.Atoi(monthsStr)
	if err != nil || months <= 0 {
		months = 6 // Default to the last 6 months
	}

	heatmapData, err := a.ActivityService.DB.HeatmapForUser(user.ID, months)
	if err != nil {
		log.Println("activity controller: Error fetching heatmap data:", err)
		respondWithError(w, http.StatusInternalServerError, "Failed to fetch activity data")
		return
	}

	respondWithJSON(w, http.StatusOK, heatmapData)
}
