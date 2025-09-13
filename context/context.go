package context

import (
	"context"

	"github.com/pranav244872/dsa-recall/models"
)

// privateKey is an unexported type to be used as a key for context values.
// This prevents collisions with other packages.
type privateKey string

// userKey is the key we will use to store and retrieve a user in the context.
const userKey privateKey = "user"

// WithUser adds a user to the context.
func WithUser(ctx context.Context, user *models.User) context.Context {
	return context.WithValue(ctx, userKey, user)
}

// User retrieves a user from the context. It returns nil if the user is not found.
func User(ctx context.Context) *models.User {
	value := ctx.Value(userKey)
	if value == nil {
		return nil
	}

	user, ok := value.(*models.User)
	if !ok {
		return nil
	}
	return user
}
