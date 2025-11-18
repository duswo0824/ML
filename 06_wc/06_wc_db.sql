show tables; -- favor_menu 라는 테이블이 있는지 확인

select * from favor_menu; -- 테이블 안의 데이터

-- 데이터에 ,(콤마) 가 들어간 것이 있음

select * from favor_menu where 메뉴 is null;
-- delete from favor_menu where 메뉴 is null; -- 메뉴가 공백인것 삭제