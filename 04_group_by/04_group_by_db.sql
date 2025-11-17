show databases;

show tables;

select * from current_dept_emp limit 5; -- 현재 부서에 속한 사원
-- emp_no(사원번호), dept_no(부서번호), from date(근무 시작 날짜), to_date(근무 종료 날짜_현재 근무 중 보통 '9999-01-01' 로 표시)
select * from departments limit 5; -- 부서의 정보 
-- dept_no(부서번호), dept_name(부서이름)
select * from dept_emp limit 5; -- 사원과 부서의 관계 (즉, 사원이 부서에 속한 이력, 부서이동의 경우 보여짐)
-- emp_no(사원번호), dept_no(부서번호), from date(근무 시작 날짜), to_date(근무 종료 날짜)
select * from dept_manager limit 5; -- 각 부서의 팀장(매니저)
-- emp_no(사원번호), dept_no(부서번호), from date(근무 시작 날짜), to_date(근무 종료 날짜)
select * from employees limit 5; -- 사원의 기본 정보
-- emp_no(사원번호), birth_date(생년월일), first_name(이름), last_name(성), gender(성별), hire_date(입사일)
select * from salaries limit 5; -- 사원의 급여
-- emp_no(사원번호), salary(급여), from date(근무 시작 날짜), to_date(근무 종료 날짜)
select * from titles limit 5; -- 사원의 직책
-- emp_no(사원번호), title(직책), from date(근무 시작 날짜), to_date(근무 종료 날짜)


-- emp_no, dept_no, dept_name, name, hire_date, salary

select e.emp_no, concat(e.first_name,e.last_name) as name, e.hire_date  from employees e;

select de.emp_no, de.dept_no from dept_emp de where de.to_date = '9999-01-01';

select d.dept_no, d.dept_name from departments d;

select s.emp_no, s.salary from salaries s where s.to_date = '9999-01-01';

-- join me!!
select 
	e.emp_no, 
	de.dept_no,
	d.dept_name,
	concat(e.first_name,',',e.last_name) as name, 
	e.hire_date,
	s.salary
from employees e join dept_emp de on e.emp_no = de.emp_no
	join salaries s on e.emp_no = s.emp_no join departments d on de.dept_no = d.dept_no
where de.to_date = '9999-01-01' and s.to_date = '9999-01-01'; -- 현재 부서와 급여

-- 수업에서 (join과 상하관계 쿼리 사용)
select 
	ce.emp_no
	,cde.dept_no 
	,(select dept_name from departments d where d.dept_no = cde.dept_no) as team_name
	,concat(e.first_name,',',e.last_name) as name
	,e.hire_date
	,s.salary
from (select emp_no from dept_emp_latest_date where to_date = '9999-01-01') ce -- latest(최근) 근속에 관련된 내용
	join employees e on ce.emp_no = e.emp_no
	join current_dept_emp cde on ce.emp_no = cde.emp_no 
	join salaries s on ce.emp_no = s.emp_no 
where s.to_date = '9999-01-01';



