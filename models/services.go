package models

import (
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

type Services struct {
	dbCon           *gorm.DB
	UserService     *UserService
	ProblemService  *ProblemService
	ActivityService *ActivityService
}

func NewServices(connectionInfo string) (*Services, error) {
	dbCon, err := gorm.Open(postgres.Open(connectionInfo), &gorm.Config{
		Logger: logger.Default.LogMode(logger.Info),
	})
	if err != nil {
		return nil, err
	}

	us, err := NewUserService(dbCon)
	if err != nil {
		return nil, err
	}

	ps, err := NewProblemService(dbCon)
	if err != nil {
		return nil, err
	}

	as := NewActivityService(dbCon)

	return &Services{
		dbCon:           dbCon,
		UserService:     us,
		ProblemService:  ps,
		ActivityService: as,
	}, err
}

func (s *Services) Close() error {
	sqlDB, err := s.dbCon.DB()
	if err != nil {
		return err
	}

	return sqlDB.Close()
}

// runs the GORM auto-migration.
func (s *Services) AutoMigrate() error {
	if err := s.dbCon.AutoMigrate(&User{}, &Problem{}, &Activity{}); err != nil {
		return err
	}
	return nil
}

// drops and rebuilds the user table.
func (s *Services) DestructiveReset() error {
	if err := s.dbCon.Migrator().DropTable(&User{}, &Problem{}, &Activity{}); err != nil {
		return err
	}
	return s.AutoMigrate()
}
