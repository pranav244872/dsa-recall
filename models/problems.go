package models

import (
	"errors"
	"time"

	"net/url"

	"gorm.io/gorm"
)

///////////////////////////////////////////////////////////////////////////////
// Problem Model
///////////////////////////////////////////////////////////////////////////////

type Problem struct {
	gorm.Model

	UserID uint `gorm:"not null;index"`

	User User `gorm:"constraint:OnUpdate:CASCADE,OnDelete:SET NULL;"`

	Title          string `gorm:"not null"`
	Link           string `gorm:"not null;uniqueIndex"`
	Approach       string `gorm:"type:text"`
	Code           string `gorm:"type:text"`
	Language       string
	CurrentStreak  int
	NextReviewDate time.Time `gorm:"type:date"`
}

///////////////////////////////////////////////////////////////////////////////
// Database Layer Interface
///////////////////////////////////////////////////////////////////////////////

type ProblemDB interface {
	// Create
	Create(problem *Problem) error

	// Read
	ByID(id uint) (*Problem, error)
	ByUserID(userID uint, searchTerm string, page, limit int) (*PaginatedProblems, error)
	ByUserIDAndDue(userID uint, page, limit int) (*PaginatedProblems, error)

	// Update
	Update(problem *Problem) error

	// Delete
	Delete(id uint) error
}

///////////////////////////////////////////////////////////////////////////////
// Service Layer
///////////////////////////////////////////////////////////////////////////////

type ProblemService struct {
	DB ProblemDB
}

func NewProblemService(dbCon *gorm.DB) (*ProblemService, error) {
	pg := &problemGorm{db: dbCon}
	pv := newProblemValidator(pg)

	ps := &ProblemService{
		DB: pv,
	}
	return ps, nil
}

///////////////////////////////////////////////////////////////////////////////
// Validation Layer
///////////////////////////////////////////////////////////////////////////////

// problemValidator wraps the ProblemDB interface to add a validation layer.
type problemValidator struct {
	ProblemDB
}

func newProblemValidator(nextLayer ProblemDB) *problemValidator {
	return &problemValidator{
		ProblemDB: nextLayer,
	}
}

// problemValFn is a function type for validating a Problem.
type problemValFn func(*Problem) error

// runProblemValFns runs a series of validation functions on a problem.
func runProblemValFns(problem *Problem, fns ...problemValFn) error {
	for _, fn := range fns {
		if err := fn(problem); err != nil {
			return err
		}
	}
	return nil
}

// --- Validation Methods ---

// Create runs validations before creating a problem.
func (pv *problemValidator) Create(p *Problem) error {
	err := runProblemValFns(p,
		pv.userIDRequired,
		pv.titleRequired,
		pv.linkRequired,
		pv.linkFormat, // Added for URL validation
	)
	if err != nil {
		return err
	}
	return pv.ProblemDB.Create(p)
}

// Update runs validations before updating a problem.
func (pv *problemValidator) Update(p *Problem) error {
	err := runProblemValFns(p,
		pv.userIDRequired,
		pv.titleRequired,
		pv.linkRequired,
		pv.linkFormat, // Also validate on update
	)
	if err != nil {
		return err
	}
	return pv.ProblemDB.Update(p)
}

// --- Validation Functions ---

func (pv *problemValidator) userIDRequired(p *Problem) error {
	if p.UserID <= 0 {
		return errors.New("a user ID is required")
	}
	return nil
}

func (pv *problemValidator) titleRequired(p *Problem) error {
	if p.Title == "" {
		return errors.New("a title is required")
	}
	return nil
}

func (pv *problemValidator) linkRequired(p *Problem) error {
	if p.Link == "" {
		return errors.New("a link is required")
	}
	return nil
}

// linkFormat validates that the problem link is a valid URL.
func (pv *problemValidator) linkFormat(p *Problem) error {
	if p.Link == "" {
		return nil
	}
	_, err := url.ParseRequestURI(p.Link)
	if err != nil {
		return errors.New("the provided link is not a valid URL")
	}
	return nil
}

///////////////////////////////////////////////////////////////////////////////
// Database Layer
///////////////////////////////////////////////////////////////////////////////

type problemGorm struct {
	db *gorm.DB
}

// --- CRUD Operations ---

// Create
func (pg *problemGorm) Create(problem *Problem) error {
	return pg.db.Create(problem).Error
}

// Read
func (pg *problemGorm) ByID(id uint) (*Problem, error) {
	var problem Problem
	db := pg.db.Where("id = ?", id)
	err := first(db, &problem)
	if err != nil {
		return nil, err
	}
	return &problem, nil
}

type PaginatedProblems struct {
	Problems []Problem
	Total    int64
}

func (pg *problemGorm) ByUserID(userID uint, searchTerm string, page, limit int) (*PaginatedProblems, error) {
	// Build the base query with the search term
	query := pg.db.Where("user_id = ?", userID)
	if searchTerm != "" {
		query = query.Where("title ILIKE ?", "%"+searchTerm+"%")
	}

	// Get the total count of all matching records
	var total int64
	if err := query.Model(&Problem{}).Count(&total).Error; err != nil {
		return nil, err
	}

	// Get the specific page of problems using Limit and Offset
	var problems []Problem
	offset := (page - 1) * limit
	err := query.Order("created_at DESC").
		Limit(limit).
		Offset(offset).
		Find(&problems).Error
	if err != nil {
		return nil, err
	}

	// Return the complete paginated result
	return &PaginatedProblems{
		Problems: problems,
		Total:    total,
	}, nil
}

func (pg *problemGorm) ByUserIDAndDue(userID uint, page, limit int) (*PaginatedProblems, error) {
	// Build the base query for due problems
	today := time.Now().Truncate(24 * time.Hour)
	query := pg.db.Where("user_id = ?", userID).
		Where("next_review_date <= ?", today)

	// Get the total count of all matching due problems
	var total int64
	if err := query.Model(&Problem{}).Count(&total).Error; err != nil {
		return nil, err
	}

	// Get the specific page of due problems using Limit and Offset
	var problems []Problem
	offset := (page - 1) * limit
	err := query.Order("next_review_date ASC"). // Order by due date
							Limit(limit).
							Offset(offset).
							Find(&problems).Error
	if err != nil {
		return nil, err
	}

	// Return the complete paginated result
	return &PaginatedProblems{
		Problems: problems,
		Total:    total,
	}, nil
}

// Update
func (pg *problemGorm) Update(problem *Problem) error {
	return pg.db.Save(problem).Error
}

// Delete
func (pg *problemGorm) Delete(id uint) error {
	return pg.db.Delete(&Problem{}, id).Error
}
