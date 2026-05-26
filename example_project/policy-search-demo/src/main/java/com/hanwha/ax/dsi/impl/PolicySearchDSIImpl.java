package com.hanwha.ax.dsi.impl;

import com.hanwha.ax.dsi.PolicySearchDSI;
import com.hanwha.ax.mapper.PolicySearchMapper;
import com.hanwha.ax.vo.PolicySearchResultVO;
import com.hanwha.ax.vo.PolicySearchVO;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * =====================================================================
 * [DSI Impl] Data Service Interface 구현체 - 증권조회 서비스
 * =====================================================================
 *
 * 역할:
 *   - PolicySearchDSI 인터페이스의 실제 업무 로직 구현
 *   - MyBatis Mapper를 호출하여 DB 데이터 조회
 *   - 필요 시 여러 Mapper 호출 결과를 조합하는 오케스트레이션 수행
 *   - 주민번호 마스킹 등 개인정보 보호 처리
 *
 * 계층 구조:
 *   PSI → DSI → [DSI Impl] → MyBatis Mapper → DB
 * =====================================================================
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class PolicySearchDSIImpl implements PolicySearchDSI {

    /** MyBatis 매퍼 - SQL 실행 담당 */
    private final PolicySearchMapper policySearchMapper;

    /**
     * 증권 목록 조회
     * - 조회조건이 하나도 없으면 전체 조회 (최대 100건)
     * - 주민번호 입력 시 하이픈 제거 후 조회
     */
    @Override
    public List<PolicySearchResultVO> selectPolicyList(PolicySearchVO searchVO) {
        log.info("[DSI] 증권목록 조회 시작 - 조건: {}", searchVO);

        // 주민번호 정규화: 하이픈(-) 제거
        if (searchVO.getCustomerRrn() != null && !searchVO.getCustomerRrn().trim().isEmpty()) {
            String normalizedRrn = searchVO.getCustomerRrn().replaceAll("-", "").trim();
            searchVO.setCustomerRrn(normalizedRrn);
        }

        // MyBatis Mapper 호출
        List<PolicySearchResultVO> resultList = policySearchMapper.selectPolicyList(searchVO);

        // 개인정보 마스킹 처리 (주민번호 뒷자리 마스킹)
        resultList.forEach(this::applyPrivacyMasking);

        log.info("[DSI] 증권목록 조회 완료 - 조회 건수: {}", resultList.size());
        return resultList;
    }

    /**
     * 증권 단건 상세 조회
     */
    @Override
    public PolicySearchResultVO selectPolicyDetail(String policyNo) {
        log.info("[DSI] 증권상세 조회 - 증권번호: {}", policyNo);

        PolicySearchResultVO result = policySearchMapper.selectPolicyDetail(policyNo);

        if (result != null) {
            applyPrivacyMasking(result);
        }

        return result;
    }

    /**
     * 개인정보 마스킹 처리
     * - 주민등록번호: 앞 6자리 표시 후 뒷 7자리 * 처리
     * 예: 900101-1234567 → 900101-*******
     */
    private void applyPrivacyMasking(PolicySearchResultVO vo) {
        String rawRrn = vo.getCustomerRrnMasked();
        if (rawRrn == null || rawRrn.trim().isEmpty()) return;

        // 하이픈 제거 후 마스킹
        String digits = rawRrn.replaceAll("-", "");
        if (digits.length() >= 6) {
            String masked = digits.substring(0, 6) + "-*******";
            vo.setCustomerRrnMasked(masked);
        }
    }
}
