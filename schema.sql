drop table if exists users;
drop table if exists words;
drop table if exists cet4;
drop table if exists cet6;

create table users (
  id integer primary key autoincrement,
  username string not null,
  password string not null,
  email string not null,
  words string default 'cet4'
);

create table words (
    user_id  integer not null,
    word string not null,
    translation string,
    primary key(user_id, word)
);

create table cet4 (
    word string primary key not null,
    translation string not null
);

create table cet6 (
    word string primary key not null,
    translation string not null
);

create table userwords (
    id integer not null,
    book string not null,
    word string not null,
    review int not null,
    primary key(id, book, word)
)