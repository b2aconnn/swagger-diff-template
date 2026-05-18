package bacon.study.swaggerdifftemplate.controller;

import bacon.study.swaggerdifftemplate.controller.dto.UserCreateRequest;
import bacon.study.swaggerdifftemplate.controller.dto.UserResponse;
import bacon.study.swaggerdifftemplate.controller.dto.UserUpdateRequest;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/users")
public class UserController implements UserApiSpec {

    @Override
    @GetMapping("/{userId}")
    public ResponseEntity<UserResponse> getUser(@PathVariable Long userId) {
        return ResponseEntity.ok(new UserResponse(userId, "홍길동", "test@test.com", "USER", null));
    }

    @Override
    @PostMapping
    public ResponseEntity<UserResponse> createUser(@RequestBody UserCreateRequest request) {
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(new UserResponse(1L, request.name(), request.email(), "USER", null));
    }

    @Override
    @PutMapping("/{id}")
    public ResponseEntity<UserResponse> updateUser(@PathVariable Long id, @RequestBody UserUpdateRequest request) {
        return ResponseEntity.ok(new UserResponse(id, request.name(), request.email(), "USER", null));
    }

}
