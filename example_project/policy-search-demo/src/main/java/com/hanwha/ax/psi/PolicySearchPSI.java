package com.hanwha.ax.psi;

import com.hanwha.ax.dsi.PolicySearchDSI;
import com.hanwha.ax.vo.PolicySearchResultVO;
import com.hanwha.ax.vo.PolicySearchVO;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;

import java.util.List;

/**
 * =====================================================================
 * [PSI] Presentation Service Interface - 증권조회 컨트롤러
 * =====================================================================
 *
 * 역할:
 *   - 화면(View)과 업무 서비스(DSI) 사이의 인터페이스 역할
 *   - HTTP 요청을 받아 DSI로 전달하고 결과를 View에 반환
 *   - 입력 파라미터 바인딩 및 기본 유효성 검사 수행
 *
 * 계층 구조:
 *   화면 (Thymeleaf) → [PSI] → DSI → MyBatis → DB
 * =====================================================================
 */
@Slf4j
@Controller
@RequestMapping("/policy")
@RequiredArgsConstructor
public class PolicySearchPSI {

    /** DSI - Data Service Interface (업무 서비스 계층) */
    private final PolicySearchDSI policySearchDSI;

    /**
     * 증권조회 화면 진입
     * GET /policy/search
     */
    @GetMapping("/search")
    public String policySearchView(Model model) {
        log.info("[PSI] 증권조회 화면 진입");
        // 빈 검색조건 VO를 모델에 담아 화면으로 전달
        model.addAttribute("searchVO", new PolicySearchVO());
        return "policySearch";  // resources/templates/policySearch.html
    }

    /**
     * 증권조회 실행
     * POST /policy/search
     *
     * @param searchVO 조회조건 (증권번호, 고객명, 고객주민번호)
     * @param model    View에 전달할 데이터 컨테이너
     * @return 조회 결과 화면
     */
    @PostMapping("/search")
    public String policySearch(PolicySearchVO searchVO, Model model) {
        log.info("[PSI] 증권조회 요청 수신 - searchVO: {}", searchVO);

        // 주민번호 입력 시 마스킹 처리 (로그에 개인정보 노출 방지)
        String maskedRrn = maskRrn(searchVO.getCustomerRrn());
        log.info("[PSI] 조회조건 - 증권번호: {}, 고객명: {}, 주민번호: {}",
                searchVO.getPolicyNo(), searchVO.getCustomerName(), maskedRrn);

        // DSI 호출 → 업무 서비스 계층에 조회 위임
        List<PolicySearchResultVO> resultList = policySearchDSI.selectPolicyList(searchVO);
        int totalCount = resultList.isEmpty() ? 0 : resultList.get(0).getTotalCount();

        log.info("[PSI] 증권조회 결과 건수: {}", totalCount);

        // 화면에 전달할 데이터 설정
        model.addAttribute("searchVO", searchVO);
        model.addAttribute("resultList", resultList);
        model.addAttribute("totalCount", totalCount);
        model.addAttribute("searchExecuted", true);

        return "policySearch";
    }

    /**
     * 주민등록번호 마스킹 (로그 출력용)
     * 예: 900101-1234567 → 900101-*******
     */
    private String maskRrn(String rrn) {
        if (rrn == null || rrn.trim().isEmpty()) return "";
        if (rrn.length() >= 6) {
            return rrn.substring(0, 6) + "-*******";
        }
        return "***";
    }
}
