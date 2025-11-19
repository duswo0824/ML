show tables;

create table news_groups(
	idx int(8) primary key auto_increment,
	content longtext,
	target int(3)
);

desc news_groups;
select * from news_groups;

desc news_groups_target_name;
select * from news_groups_target_name tn;


-- content, target, target_name
select ng.content, ng.target from news_groups ng ;
select tn.index, tn.target_name from news_groups_target_name tn;


select ng.content, ng.target, tn.target_name	
	from news_groups ng join news_groups_target_name tn on ng.target = tn.index;







drop table news_groups;
delete from news_groups;