package com.hanwha.ax.vo;

import lombok.Getter;
import lombok.Setter;
import lombok.ToString;

/**
 * 증권조회 검색조건 VO
 * 화면에서 입력받는 조회 파라미터를 담는 객체
 */
@Getter
@Setter
@ToString
public class PolicySearchVO {

    /** 증권번호 */
    private String policyNo;

    /** 고객명 */
    private String customerName;

    /** 고객 주민등록번호 (앞 6자리만 입력 가능) */
    private String customerRrn;

    /** 페이지 번호 (기본값 1) */
    private int pageNo = 1;

    /** 페이지당 건수 (기본값 10) */
    private int pageSize = 10;
}
