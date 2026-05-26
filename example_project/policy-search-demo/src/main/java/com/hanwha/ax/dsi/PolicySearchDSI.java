package com.hanwha.ax.dsi;

import com.hanwha.ax.vo.PolicySearchResultVO;
import com.hanwha.ax.vo.PolicySearchVO;

import java.util.List;

/**
 * =====================================================================
 * [DSI] Data Service Interface - 증권조회 서비스 인터페이스
 * =====================================================================
 *
 * 역할:
 *   - PSI(컨트롤러)와 데이터 접근 계층(MyBatis Mapper) 사이의 인터페이스 정의
 *   - 업무 로직(비즈니스 규칙)을 캡슐화하는 서비스 계층의 계약(Contract)
 *   - 구현체(PolicySearchDSIImpl)와 분리하여 의존성 역전 원칙(DIP) 적용
 *
 * 계층 구조:
 *   PSI → [DSI Interface] → DSI Impl → MyBatis → DB
 * =====================================================================
 */
public interface PolicySearchDSI {

    /**
     * 증권 목록 조회
     *
     * @param searchVO 조회조건 (증권번호, 고객명, 주민번호)
     * @return 증권 목록 (각 VO에 totalCount 포함)
     */
    List<PolicySearchResultVO> selectPolicyList(PolicySearchVO searchVO);

    /**
     * 증권 단건 상세 조회
     *
     * @param policyNo 증권번호
     * @return 증권 상세 정보
     */
    PolicySearchResultVO selectPolicyDetail(String policyNo);
}
