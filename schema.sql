drop table if exists links;
create table links (
  id integer primary key autoincrement,
  url text not null,
  redirect string not null,
  hotness integer
);
