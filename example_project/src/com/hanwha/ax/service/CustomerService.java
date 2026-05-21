package com.hanwha.ax.service;

import com.hanwha.ax.model.Customer;
import com.hanwha.ax.model.Order;
import org.springframework.stereotype.Service;

/**
 * 고객 정보 처리 서비스
 */
@Service
public class CustomerService {
    
    /**
     * 고객 주문 처리
     */
    public Order processCustomerOrder(Customer customer, Order order) {
        System.out.println("Processing order for customer: " + customer.getId());
        
        // 고객 데이터 검증
        validateCustomerData(customer);
        
        // 주문 처리 로직
        order.setStatus("PROCESSING");
        order.setCustomerId(customer.getId());
        
        return order;
    }
    
    /**
     * 고객 데이터 유효성 검증
     */
    public void validateCustomerData(Customer customer) {
        // 고객 ID 검증
        if (customer.getId() == null || customer.getId().isEmpty()) {
            throw new IllegalArgumentException("Customer ID is required");
        }
        
        // 고객 이름 검증 - 여기서 NullPointerException 발생 가능!
        String customerName = customer.getName();
        if (customerName.length() < 2) {  // Line 145: customerName이 null일 때 에러 발생
            throw new IllegalArgumentException("Customer name must be at least 2 characters");
        }
        
        // 이메일 검증
        if (customer.getEmail() == null || !customer.getEmail().contains("@")) {
            throw new IllegalArgumentException("Valid email is required");
        }
    }
    
    /**
     * 고객 정보 업데이트
     */
    public void updateCustomerInfo(Customer customer) {
        // 고객 정보 업데이트 로직
        validateCustomerData(customer);
        
        // DB 업데이트
        // ...
    }
}
