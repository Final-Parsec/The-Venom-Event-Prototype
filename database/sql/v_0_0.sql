-- Schema change to user_account to allow for roles and password authorization.

create table if not exists user_account (
  `id` int(10) unsigned not null auto_increment,
  `name` varchar(20) not null,
  `password_hash` char(54) not null,
  `role` varchar(100) not null default 'free_user',
  PRIMARY KEY (`id`)
);

insert into user_account (name, password_hash, role)
values ('baer', 'sha1$jM2pd5LH$142412ca74102b46756dec275b704c61ef007341', 'admin');

insert into user_account (name, password_hash, role)
values ('Snowman', 'sha1$nwl8vErr$dc3c0889f1e7b160b906fe5ba8f364ef2225fcaa', 'admin');