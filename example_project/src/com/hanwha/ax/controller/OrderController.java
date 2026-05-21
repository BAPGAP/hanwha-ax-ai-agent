package com.hanwha.ax.controller;

import com.hanwha.ax.model.Customer;
import com.hanwha.ax.model.Order;
import com.hanwha.ax.service.CustomerService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

/**
 * 주문 처리 컨트롤러
 */
@RestController
@RequestMapping("/api/orders")
public class OrderController {
    
    @Autowired
    private CustomerService customerService;
    
    /**
     * 새 주문 생성
     */
    @PostMapping("/create")
    public Order createOrder(@RequestBody OrderRequest request) {
        // 고객 정보 조회
        Customer customer = new Customer();
        customer.setId(request.getCustomerId());
        customer.setName(request.getCustomerName());
        customer.setEmail(request.getCustomerEmail());
        
        // 주문 생성
        Order order = new Order();
        order.setProductId(request.getProductId());
        order.setQuantity(request.getQuantity());
        
        // 주문 처리 - Line 67에서 CustomerService 호출
        return customerService.processCustomerOrder(customer, order);
    }
    
    /**
     * 주문 제출
     */
    @PostMapping("/submit")
    public Order submitOrder(@RequestBody Order order) {
        // 주문 제출 로직
        return order;
    }
}
