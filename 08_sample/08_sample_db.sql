show tables; -- news_score
desc news_score;

select * from news_score ns;

-- drop table news_score;

SELECT COUNT(score)AS cnt FROM news_score;

select * from news_score ns where score >= 50;

select subject, score from news_score;