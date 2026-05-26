package com.hanwha.ax.psi;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

/**
 * 루트 경로 → 증권조회 화면으로 리다이렉트
 */
@Controller
public class RootPSI {

    @GetMapping("/")
    public String root() {
        return "redirect:/policy/search";
    }
}
