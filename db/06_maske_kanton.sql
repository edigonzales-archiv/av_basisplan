-- Table: av_basisplan.maske_kanton

-- DROP TABLE av_basisplan.maske_kanton;

CREATE TABLE av_basisplan.maske_kanton
(
  ogc_fid serial NOT NULL,
  geometrie geometry,
  datenstand date,
  art character varying(50),
  ktnr integer,
  CONSTRAINT maske_kanton_pkey PRIMARY KEY (ogc_fid),
  --???? gab probleme beim copy/pasten von kt sz CONSTRAINT enforce_dims_geometrie CHECK (st_ndims(geometrie) = 2),
  CONSTRAINT enforce_geotype_geometrie CHECK (geometrytype(geometrie) = 'MULTIPOLYGON'::text OR geometrie IS NULL),
  CONSTRAINT enforce_srid_geometrie CHECK (st_srid(geometrie) = 21781)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE av_basisplan.maske_kanton OWNER TO stefan;
GRANT ALL ON TABLE av_basisplan.maske_kanton TO stefan;
GRANT SELECT ON TABLE av_basisplan.maske_kanton TO mspublic;
