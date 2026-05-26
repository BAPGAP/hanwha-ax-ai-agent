-- =====================================================================
-- [DB Schema] 증권조회 데모 테이블 정의
-- H2 In-Memory Database 용 DDL
-- =====================================================================

-- 고객 기본 테이블
CREATE TABLE IF NOT EXISTS TB_CUSTOMER (
    CUSTOMER_ID   VARCHAR(20)  NOT NULL PRIMARY KEY,  -- 고객ID
    CUSTOMER_NAME VARCHAR(50)  NOT NULL,               -- 고객명
    CUSTOMER_RRN  VARCHAR(14)  NOT NULL,               -- 주민등록번호 (숫자 13자리)
    PHONE_NO      VARCHAR(20),                         -- 연락처
    EMAIL         VARCHAR(100),                        -- 이메일
    ADDRESS       VARCHAR(200),                        -- 주소
    REG_DATE      DATE         DEFAULT CURRENT_DATE    -- 등록일
);

-- 증권 기본 테이블
CREATE TABLE IF NOT EXISTS TB_POLICY (
    POLICY_NO          VARCHAR(20)  NOT NULL PRIMARY KEY, -- 증권번호
    CUSTOMER_ID        VARCHAR(20)  NOT NULL,              -- 고객ID (FK)
    PRODUCT_CODE       VARCHAR(20)  NOT NULL,              -- 상품코드
    PRODUCT_NAME       VARCHAR(100) NOT NULL,              -- 상품명
    CONTRACT_DATE      DATE         NOT NULL,              -- 계약일자
    START_DATE         DATE         NOT NULL,              -- 보험시작일
    END_DATE           DATE         NOT NULL,              -- 보험만기일
    CONTRACT_PERIOD    VARCHAR(20)  NOT NULL,              -- 가입기간
    MONTHLY_PREMIUM    BIGINT       NOT NULL DEFAULT 0,    -- 월 보험료
    COVERAGE_AMOUNT    BIGINT       NOT NULL DEFAULT 0,    -- 보장금액
    PAYMENT_CYCLE      VARCHAR(10)  NOT NULL DEFAULT '월납', -- 납입주기
    PAYMENT_METHOD     VARCHAR(20)  NOT NULL DEFAULT '자동이체', -- 납입방법
    CONTRACT_STATUS    VARCHAR(20)  NOT NULL DEFAULT '정상', -- 계약상태
    CONTRACT_STATUS_CD VARCHAR(10)  NOT NULL DEFAULT 'N',  -- 상태코드 (N:정상/E:실효/T:해지/X:만기)
    AGENT_NAME         VARCHAR(50),                        -- 담당 설계사명
    BRANCH_NAME        VARCHAR(50),                        -- 담당 지점명
    CONSTRAINT FK_POLICY_CUSTOMER FOREIGN KEY (CUSTOMER_ID) REFERENCES TB_CUSTOMER(CUSTOMER_ID)
);
