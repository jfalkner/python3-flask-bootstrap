INSERT INTO site (name, contact, address, state_or_region, country, postcode_or_zip)
    VALUES ( 'Site 1' , 'John Smith', '123 Muffin Lane, Ann Arbor', 'MI', 'USA', '48103');
INSERT INTO site (name) VALUES ( 'Site 2' );
INSERT INTO site (name) VALUES ( 'Site 3' );

-- some instruments (freezers and computers)
INSERT INTO computer (site_id, name) VALUES 
    ( 1, 'Computer 1' ),
    ( 1, 'Computer 2' );
INSERT INTO freezer (site_id, name) VALUES 
    ( 1, '-20C' ),
    ( 1, '-40C' );
