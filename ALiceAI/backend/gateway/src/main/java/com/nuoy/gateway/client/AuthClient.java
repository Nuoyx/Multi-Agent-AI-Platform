package com.nuoy.gateway.client;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.service.annotation.GetExchange;
import org.springframework.web.service.annotation.PostExchange;


public interface AuthClient {
  
  @GetExchange("/")
  String health();

  @PostExchange("/login")
ResponseEntity<String> login(@RequestBody LoginRequest request);
}
