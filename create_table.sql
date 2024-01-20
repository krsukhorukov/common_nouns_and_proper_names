
CREATE TABLE company_detect_conversion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    `count` INT,
    phone_number bigint unsigned
);

create table is_company
(
    phone_number bigint unsigned                                    not null comment 'Номер телефона',
    type         enum ('ban', 'tag', 'incoming_call', 'moderation', 'contacts') not null comment 'Тип определения (баны, тег компания, входящие звонки, модерация, контакты)',
    status       tinyint(1)                                         not null comment 'Статус',
    updated_at   datetime default CURRENT_TIMESTAMP                 not null comment 'Дата последнего обновления',
    constraint is_company_phone_number_type_uindex
        unique (phone_number, type)
);