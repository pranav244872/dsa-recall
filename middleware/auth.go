package middleware

import (
	"net/http"

	"github.com/pranav244872/dsa-recall/context"
	"github.com/pranav244872/dsa-recall/models"
)

type User struct {
	UserService *models.UserService
}

func (u *User) Require(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// check for remember_token cookie
		cookie, err := r.Cookie("remember_token")
		if err != nil {
			http.Error(w, "Unauthorized - no token", http.StatusUnauthorized)
			return
		}

		user, err := u.UserService.DB.ByRememberToken(cookie.Value)
		if err != nil {
			http.Error(w, "Unauthorized - invalid token", http.StatusUnauthorized)
			return
		}

		ctx := context.WithUser(r.Context(), user)

		next.ServeHTTP(w, r.WithContext(ctx))
	})
}
