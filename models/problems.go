package models

import (
	"time"

	"gorm.io/gorm"
)

type Problem struct {
	gorm.Model // ID, CreatedAt, UpdatedAt, DeletedAt

	UserID uint `gorm:"not null;index"` // FK

	User User `gorm:"constraint:OnUpdate:CASCADE,OnDelete:SET NULL;"`

	Title          string `gorm:"not null"`
	Link           string `gorm:"not null;uniqueIndex"`
	Approach       string `gorm:"type:text"`
	Code           string `gorm:"type:text"`
	CurrentStreak  int
	NextReviewDate time.Time `gorm:"type:date"`
}

///////////////////////////////////////////////////////////////////////////////
// Database layer interface
///////////////////////////////////////////////////////////////////////////////

type ProblemDB interface {
	// Create
	Create(problem *Problem) error
}

///////////////////////////////////////////////////////////////////////////////
// Service Layer
///////////////////////////////////////////////////////////////////////////////

type ProblemService struct {
	DB ProblemDB
}

func NewProblemService(dbCon *gorm.DB) (*ProblemService, error) {
	pg := &problemGorm{db: dbCon}

	// create validation layer
	pv := newProblemValidator(pg)

	// Create service layer
	ps := &ProblemService{
		DB: pv,
	}
	return ps, nil
}

///////////////////////////////////////////////////////////////////////////////
// Validation Layer
///////////////////////////////////////////////////////////////////////////////

type problemValidator struct {
	ProblemDB
}

func newProblemValidator(nextLayer ProblemDB) *problemValidator {
	return &problemValidator{
		ProblemDB: nextLayer,
	}
}

///////////////////////////////////////////////////////////////////////////////
// Database Layer
///////////////////////////////////////////////////////////////////////////////

// this is implementation of ProblemDB interface
type problemGorm struct {
	db *gorm.DB
}

// --- CRUD operations ---

// Create problem
func (pg *problemGorm) Create(problem *Problem) error {
	return pg.db.Create(problem).Error
}
