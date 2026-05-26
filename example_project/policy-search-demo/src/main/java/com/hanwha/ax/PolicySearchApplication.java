package com.hanwha.ax;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * 한화AX 증권조회 데모 애플리케이션
 *
 * 계층 구조:
 *   화면 (Thymeleaf HTML)
 *     ↓
 *   PSI - Presentation Service Interface (Controller)
 *     ↓
 *   DSI - Data Service Interface (Service)
 *     ↓
 *   MyBatis Mapper (SQL)
 *     ↓
 *   DB (H2 In-Memory)
 */
@SpringBootApplication
@MapperScan("com.hanwha.ax.mapper")
public class PolicySearchApplication {

    public static void main(String[] args) {
        SpringApplication.run(PolicySearchApplication.class, args);
    }
}
