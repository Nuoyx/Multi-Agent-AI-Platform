package com.nuoy.gateway.client;

import org.springframework.web.service.annotation.GetExchange;

public interface AuthClient {
  
  @GetExchange("/")
  String health();
}
