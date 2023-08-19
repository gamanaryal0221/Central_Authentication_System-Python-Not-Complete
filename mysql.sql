create user
    'rm' @'localhost' identified by 'rm';

grant all privileges on *.* to 'rm'@'localhost';

flush privileges;

create database resource_manager_dev;

create table
    `resource_manager_dev`.`client` (
        `id` bigint not null auto_increment primary key,
        `soft_deleted` boolean not null default false,
        `name` varchar(255) not null,
        `display_name` varchar(500) null,
        `registered_id` varchar(20) not null,
        `created_at` timestamp not null default current_timestamp,
        `is_google_authentication_enabled` boolean not null default false,
        `is_credential_authentication_enabled` boolean not null default true
    );

create table
    `resource_manager_dev`.`client_email` (
        `id` bigint not null auto_increment primary key,
        `soft_deleted` boolean not null default false,
        `client_id` bigint not null,
        `email` varchar(255) not null,
        `is_primary` boolean not null default false,
        `created_at` timestamp not null default current_timestamp,
        foreign key (client_id) references `resource_manager_dev`.`client` (id)
    );

create table
    `resource_manager_dev`.`client_number` (
        `id` bigint not null auto_increment primary key,
        `soft_deleted` boolean not null default false,
        `client_id` bigint not null,
        `country_code` varchar(5) null,
        `number` varchar(10) not null,
        `is_primary` boolean not null default false,
        `created_at` timestamp not null default current_timestamp,
        foreign key (client_id) references `resource_manager_dev`.`client` (id)
    );

create table
    `resource_manager_dev`.`service` (
        `id` bigint not null auto_increment primary key,
        `soft_deleted` boolean not null default false,
        `name` varchar(255) not null,
        `display_name` varchar(500) null,
        `created_at` timestamp not null default current_timestamp
    );

create table
    `resource_manager_dev`.`client_service` (
        `id` bigint not null auto_increment primary key,
        `client_id` bigint not null,
        `service_id` bigint not null,
        `request_host` varchar(500) not null,
        `created_at` timestamp not null default current_timestamp,
        foreign key (client_id) references `resource_manager_dev`.`client` (id),
        foreign key (service_id) references `resource_manager_dev`.`service` (id)
    );

use resource_manager_dev;
insert into client(name, display_name, registered_id)
values ("admin", "Admin", "VCP12345");
insert into client_number(client_id, country_code, number, is_primary)
values ((select id from client where name="admin"), "+977", "9848765833", true);
insert into client_email(client_id, email, is_primary)
values ((select id from client where name="admin"), "admin@vpc.com", true);
insert into service(name, display_name)
values ("rm", "Resource Manager");
insert into client_service(client_id, service_id, request_host)
values ((select id from client where name="admin"), (select id from service where name="rm"), "admin.rm.dev.vcp.com");


create table
    `resource_manager_dev`.`user` (
        `id` bigint not null auto_increment primary key,
        `username` varchar(255) not null unique,
        `first_name` varchar(255) not null,
        `middle_name` varchar(255) null,
        `last_name` varchar(255) not null,
        `gender` int not null,
        `salt_value` varchar(255) not null,
        `password` varchar(500) not null
    );

create table
    `resource_manager_dev`.`user_email` (
        `id` bigint not null auto_increment primary key,
        `user_id` bigint not null,
        `email` varchar(255) not null,
        `is_primary` boolean not null default false,
        foreign key (user_id) references `resource_manager_dev`.`user` (id)
    );

create table
    `resource_manager_dev`.`user_number` (
        `id` bigint not null auto_increment primary key,
        `user_id` bigint not null,
        `country_code` varchar(5) null,
        `number` varchar(255) not null,
        `is_primary` boolean not null default false,
        foreign key (user_id) references `resource_manager_dev`.`user` (id)
    );

create table
    `resource_manager_dev`.`user_client_service` (
        `id` bigint not null auto_increment primary key,
        `client_service_id` bigint not null,
        `user_id` bigint not null,
        `created_at` timestamp not null default current_timestamp,
        foreign key (client_service_id) references `resource_manager_dev`.`client_service` (id),
        foreign key (user_id) references `resource_manager_dev`.`user` (id)
    );

use resource_manager_dev;
insert into user(username, first_name, last_name, gender, salt_value, password)
values ("gaman0221", "Gaman", "Aryal", 1, "$2b$12$9nvNNxOWaKDnfIDfxE1s7O", "$2b$12$9nvNNxOWaKDnfIDfxE1s7OrJERiS4RN.6yXkMRtOFQjOn8Gv.FKs6");
insert into user_number(user_id, country_code, number, is_primary)
values ((select id from user where username="gaman0221"), "+977", "9848765833", true);
insert into user_email(user_id, email, is_primary)
values ((select id from user where username="gaman0221"), "gaman.aryal@gmail.com", true);
insert into user_client_service(user_id, client_service_id)
values ((select id from user where username="gaman0221"), (select id from client_service where request_host="admin.rm.dev.vcp.com"));




create table
    `resource_manager_dev`.`user_photo` (
        `id` bigint not null auto_increment primary key,
        `user_id` bigint not null,
        `photo_url` varchar(1000) not null,
        `is_primary` boolean not null default false,
        foreign key (user_id) references `resource_manager_dev`.`user` (id)
    );

create table
    `resource_manager_dev`.`client` (
        `id` bigint not null auto_increment primary key,
        `name` varchar(255) not null,
        `display_name` varchar(500) null,
        `registered_id` varchar(20) not null
    );

create table
    `resource_manager_dev`.`client_email` (
        `id` bigint not null auto_increment primary key,
        `client_id` bigint not null,
        `email` varchar(255) not null,
        `is_primary` boolean not null default false,
        foreign key (client_id) references `resource_manager_dev`.`client` (id)
    );

create table
    `resource_manager_dev`.`client_number` (
        `id` bigint not null auto_increment primary key,
        `client_id` bigint not null,
        `country_code` varchar(5) null,
        `number` varchar(255) not null,
        `is_primary` boolean not null default false,
        foreign key (client_id) references `resource_manager_dev`.`client` (id)
    );

create table
    `resource_manager_dev`.`chat` (
        `id` bigint not null auto_increment primary key,
        `is_group_chat` boolean not null default false,
        `name` varchar(255),
        `created_at` timestamp not null default current_timestamp,
        `created_by` bigint not null,
        foreign key (created_by) references `resource_manager_dev`.`user` (id)
    );

create table
    `resource_manager_dev`.`chat_member` (
        `id` bigint not null auto_increment primary key,
        `chat_id` bigint not null,
        `user1_id` bigint not null,
        `user2_id` bigint not null,
        `user1_joined_at` timestamp,
        `user2_joined_at` timestamp,
        foreign key (chat_id) references `resource_manager_dev`.`chat` (id),
        foreign key (user1_id) references `resource_manager_dev`.`user` (id),
        foreign key (user2_id) references `resource_manager_dev`.`user` (id)
    );

create table
    `resource_manager_dev`.`group_chat_member` (
        `id` bigint not null auto_increment primary key,
        `chat_id` bigint not null,
        `user_id` bigint not null,
        `is_admin` boolean not null default false,
        `joined_at` timestamp not null default now(),
        `added_by` bigint not null,
        foreign key (chat_id) references `resource_manager_dev`.`chat` (id),
        foreign key (user_id) references `resource_manager_dev`.`user` (id),
        foreign key (added_by) references `resource_manager_dev`.`user` (id)
    );

create table
    `resource_manager_dev`.`message` (
        `id` bigint not null auto_increment primary key,
        `chat_id` bigint not null,
        `sender_id` bigint not null,
        `message` text,
        `sent_at` timestamp default current_timestamp,
        `delivered_at` timestamp default current_timestamp,
        foreign key (chat_id) references `resource_manager_dev`.`chat` (id),
        foreign key (sender_id) references `resource_manager_dev`.`user` (id)
    );