-- View: av_basisplan.nomenklatur_gelaendename_v

-- DROP VIEW av_basisplan.nomenklatur_gelaendename_v;

CREATE OR REPLACE VIEW av_basisplan.nomenklatur_gelaendename_v AS 
 SELECT pos.ogc_fid, pos.tid, pos.gelaendenamepos_von, pos.pos, 
        CASE
            WHEN pos.ori IS NULL THEN 100::double precision
            ELSE pos.ori
        END AS ori, pos.hali_txt, pos.vali_txt, pos.groesse_txt, pos.stil_txt, pos.gem_bfs, pos.los, pos.lieferdatum, gname.name, st_x(pos.pos) AS xlabel, st_y(pos.pos) AS ylabel
   FROM av_avdpool_ch.nomenklatur_gelaendenamepos pos, av_avdpool_ch.nomenklatur_gelaendename gname
  WHERE gname.tid::text = pos.gelaendenamepos_von::text;

ALTER TABLE av_basisplan.nomenklatur_gelaendename_v OWNER TO stefan;
GRANT ALL ON TABLE av_basisplan.nomenklatur_gelaendename_v TO stefan;
GRANT SELECT ON TABLE av_basisplan.nomenklatur_gelaendename_v TO mspublic;

