package com.nuoy.gateway;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.service.registry.ImportHttpServices;
import com.nuoy.gateway.client.AuthClient;

@SpringBootApplication
@ImportHttpServices(group = "auth", types = AuthClient.class)
public class GatewayApplication {

    public static void main(String[] args) {
        SpringApplication.run(GatewayApplication.class, args);
    }

}
