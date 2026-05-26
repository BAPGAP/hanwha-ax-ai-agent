package com.hanwha.ax.mapper;

import com.hanwha.ax.vo.PolicySearchResultVO;
import com.hanwha.ax.vo.PolicySearchVO;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

/**
 * =====================================================================
 * [MyBatis Mapper] 증권조회 매퍼 인터페이스
 * =====================================================================
 *
 * 역할:
 *   - MyBatis가 관리하는 SQL 매퍼 인터페이스
 *   - 실제 SQL은 PolicySearchMapper.xml에 정의
 *   - DSI Impl에서 이 인터페이스를 호출하면 MyBatis가 XML SQL을 실행
 *
 * 계층 구조:
 *   PSI → DSI → DSI Impl → [MyBatis Mapper] → DB
 *
 * 매핑 XML: resources/mapper/PolicySearchMapper.xml
 * =====================================================================
 */
@Mapper
public interface PolicySearchMapper {

    /**
     * 증권 목록 조회
     * SQL ID: selectPolicyList
     *
     * @param searchVO 조회조건 VO
     * @return 증권 목록
     */
    List<PolicySearchResultVO> selectPolicyList(PolicySearchVO searchVO);

    /**
     * 증권 단건 상세 조회
     * SQL ID: selectPolicyDetail
     *
     * @param policyNo 증권번호
     * @return 증권 상세 정보
     */
    PolicySearchResultVO selectPolicyDetail(String policyNo);
}
