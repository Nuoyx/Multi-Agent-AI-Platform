package com.nuoy.gateway.controller;

import com.nuoy.gateway.client.AuthClient;

import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/api/auth")
public class AuthGatewayController {

  private final AuthClient authClient;

  public AuthGatewayController(AuthClient authClient) {
    this.authClient = authClient;
  }

  @GetMapping("/health")
  public String health() {
    try {
      return authClient.health();
    } catch (ResourceAccessException ex) {
      throw new ResponseStatusException(
          HttpStatus.SERVICE_UNAVAILABLE, "Auth service is unreachable", ex);
    }
  }
}
