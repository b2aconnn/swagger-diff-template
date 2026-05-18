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
    @GetMapping("/{id}")
    public ResponseEntity<UserResponse> getUser(@PathVariable Long id) {
        return ResponseEntity.ok(new UserResponse(id, "홍길동", "test@test.com"));
    }

    @Override
    @PostMapping
    public ResponseEntity<UserResponse> createUser(@RequestBody UserCreateRequest request) {
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(new UserResponse(1L, request.name(), request.email()));
    }

    @Override
    @PutMapping("/{id}")
    public ResponseEntity<UserResponse> updateUser(@PathVariable Long id, @RequestBody UserUpdateRequest request) {
        return ResponseEntity.ok(new UserResponse(id, request.name(), request.email()));
    }

    @Override
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteUser(@PathVariable Long id) {
        return ResponseEntity.noContent().build();
    }
}
