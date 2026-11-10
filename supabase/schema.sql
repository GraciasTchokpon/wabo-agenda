-- Wabo – Agenda Bénin : schéma de base de données (PostgreSQL / Supabase)
-- À exécuter une fois dans Supabase > SQL Editor.

create extension if not exists pg_trgm;

-- 1. Sources suivies par la veille ------------------------------------------
create table if not exists sources (
  id           bigserial primary key,
  name         text not null,
  kind         text not null check (kind in ('whatsapp','formulaire','site','rss','instagram','manuel','partenaire')),
  url          text,
  frequency    text default 'quotidienne',
  reliability  real not null default 0.5 check (reliability between 0 and 1),
  active       boolean not null default true,
  created_at   timestamptz not null default now()
);

insert into sources (name, kind, reliability) values
  ('WhatsApp Wabo', 'whatsapp', 0.6),
  ('Formulaire du site', 'formulaire', 0.6),
  ('Saisie manuelle', 'manuel', 0.9)
on conflict do nothing;

-- 2. Tout ce qui entre, tel quel ---------------------------------------------
create table if not exists raw_items (
  id                bigserial primary key,
  source_id         bigint references sources(id),
  received_at       timestamptz not null default now(),
  text              text,
  media_urls        text[] default '{}',
  origin_url        text,
  submitter_contact text,
  content_hash      text unique,
  status            text not null default 'nouveau'
                    check (status in ('nouveau','extrait','traite','rejete','erreur')),
  error             text
);
create index if not exists raw_items_status_idx on raw_items(status);

-- 3. Ce que l'IA a lu dans chaque élément -------------------------------------
create table if not exists extractions (
  id           bigserial primary key,
  raw_item_id  bigint not null references raw_items(id) on delete cascade,
  data         jsonb not null,
  confidence   real,
  warnings     text[] default '{}',
  model        text,
  event_id     text,
  created_at   timestamptz not null default now()
);

-- 4. Lieux et organisateurs normalisés ---------------------------------------
create table if not exists venues (
  id        bigserial primary key,
  name      text not null,
  aliases   text[] default '{}',
  district  text,
  city      text not null,
  lat       double precision,
  lng       double precision
);

create table if not exists organizers (
  id              bigserial primary key,
  name            text not null,
  aliases         text[] default '{}',
  public_contact  text,
  socials         jsonb default '{}',
  verified        boolean not null default false
);

-- 5. Les événements publiés ---------------------------------------------------
create table if not exists events (
  id            text primary key,                 -- identifiant lisible, ex. vodun-days-2027
  title         text not null,
  category      text not null,
  start_date    date not null,
  end_date      date not null,
  start_time    text,
  city          text not null,
  place         text not null,
  price_text    text not null default 'Non communiqué',
  is_free       boolean not null default false,
  dates_tbc     boolean not null default false,
  date_text     text,
  description   text not null default '',
  link          text,
  sources       jsonb not null default '[]',      -- [{label, url}]
  status        text not null default 'a_valider'
                check (status in ('a_valider','publie','rejete','annule')),
  confidence    real,
  venue_id      bigint references venues(id),
  organizer_id  bigint references organizers(id),
  verified_at   timestamptz,
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now(),
  check (end_date >= start_date)
);
create index if not exists events_dates_idx on events(start_date, end_date);
create index if not exists events_status_idx on events(status);
create index if not exists events_title_trgm on events using gin (title gin_trgm_ops);

-- Un événement peut être vu par plusieurs sources
create table if not exists event_sources (
  event_id     text references events(id) on delete cascade,
  raw_item_id  bigint references raw_items(id) on delete cascade,
  primary key (event_id, raw_item_id)
);

create or replace function touch_updated_at() returns trigger language plpgsql as $$
begin new.updated_at = now(); return new; end $$;
drop trigger if exists events_touch on events;
create trigger events_touch before update on events for each row execute function touch_updated_at();

-- 6. Sécurité : le public ne lit que les événements publiés ----------------------
-- Les écritures passent par le serveur (clé service_role), jamais par le navigateur.
alter table events enable row level security;
alter table raw_items enable row level security;
alter table extractions enable row level security;
alter table sources enable row level security;
alter table venues enable row level security;
alter table organizers enable row level security;
alter table event_sources enable row level security;

drop policy if exists "lecture publique des événements publiés" on events;
create policy "lecture publique des événements publiés" on events
  for select to anon, authenticated using (status in ('publie','annule'));

drop policy if exists "lecture publique des lieux" on venues;
create policy "lecture publique des lieux" on venues for select to anon, authenticated using (true);

-- 7. Stockage public des affiches reçues par WhatsApp ---------------------------
insert into storage.buckets (id, name, public) values ('affiches', 'affiches', true)
on conflict (id) do nothing;
