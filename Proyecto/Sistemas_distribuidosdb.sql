create database sistemas_dis;
use sistemas_dis;

create table users(
	id int not null primary key auto_increment,
    name varchar(20),
    password varchar(20)
);

drop table users;

insert into users(name, password) values('cesar', 'cesar123');
insert into users(name, password) values('juan', 'juan123');
select * from users;