// in backend/models/activity.go

package models

import (
	"time"

	"gorm.io/gorm"
)

///////////////////////////////////////////////////////////////////////////////
// Activity Model
///////////////////////////////////////////////////////////////////////////////

type Activity struct {
	gorm.Model
	UserID     uint      `gorm:"not null;index"`
	ProblemID  uint      `gorm:"not null"`
	ReviewedAt time.Time `gorm:"not null"`
}

type HeatmapData struct {
	Date  time.Time `json:"date"`
	Count int       `json:"count"`
}

///////////////////////////////////////////////////////////////////////////////
// Database layer interface
///////////////////////////////////////////////////////////////////////////////

type ActivityDB interface {
	// Create
	Create(activity *Activity) error

	// Read
	HeatmapForUser(userID uint, months int) ([]HeatmapData, error)
}

///////////////////////////////////////////////////////////////////////////////
// Service Layer
///////////////////////////////////////////////////////////////////////////////

type ActivityService struct {
	DB ActivityDB
}

func NewActivityService(db *gorm.DB) *ActivityService {
	ag := &activityGorm{db: db}
	return &ActivityService{DB: ag}
}

///////////////////////////////////////////////////////////////////////////////
// Database Layer
///////////////////////////////////////////////////////////////////////////////

type activityGorm struct {
	db *gorm.DB
}

func (ag *activityGorm) Create(activity *Activity) error {
	return ag.db.Create(activity).Error
}

func (ag *activityGorm) HeatmapForUser(userID uint, months int) ([]HeatmapData, error) {
	var results []HeatmapData

	startDate := time.Now().AddDate(0, -months, 0)

	err := ag.db.Raw(`
		SELECT DATE(reviewed_at) as date, COUNT(*) as count
		FROM activities
		WHERE user_id = ? AND reviewed_at >= ?
		GROUP BY date
		ORDER BY date ASC`, userID, startDate).Scan(&results).Error

	return results, err
}
