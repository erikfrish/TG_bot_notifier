CREATE TABLE IF NOT EXISTS "Tasks_audit" (
    operation         char(10)   NOT NULL,
    task_id           BIGINT NOT NULL,
    stamp             timestamp with time zone DEFAULT now(),
    task_header       character varying(100),
    old_status        character varying(20),
    new_status        character varying(20),
    customer          integer,
    old_executor      integer,
    new_executor      integer,
    mentor            integer, 
    task_deadline     timestamp with time zone,
    task_body         text, --character varying(100),
    near_university   BOOLEAN,
    who_notify_in_tg  char(10)
);
-- COMMENT ON COLUMN "Tasks_audit".task_deadline IS 'if changed';

CREATE OR REPLACE FUNCTION "process_Tasks_audit"() RETURNS TRIGGER AS $Tasks_audit$
    BEGIN
        -- Добавление строки в "Tasks_audit", которая отражает операцию, выполняемую в Tasks;
        -- для определения типа операции применяется специальная переменная TG_OP.

        IF (TG_OP = 'DELETE') THEN
            INSERT INTO "Tasks_audit" (operation, task_id, task_header, old_status, customer, old_executor, mentor, task_deadline, task_body, near_university, who_notify_in_tg)
            SELECT 'D', OLD.id, OLD.header, OLD.status, OLD.customer, OLD.executor, OLD.mentor, OLD.dedline, OLD.task, OLD.university, OLD.executor;

        ELSIF (TG_OP = 'INSERT') THEN
            NEW.last_changes = now();
            INSERT INTO "Tasks_audit" (operation, task_id, task_header, new_status, customer, new_executor, mentor, task_deadline, task_body, near_university, who_notify_in_tg)
            SELECT 'I', NEW.id, NEW.header, NEW.status, NEW.customer, NEW.executor, NEW.mentor, NEW.dedline, NEW.task, NEW.university, NEW.executor; 

        ELSIF (TG_OP = 'UPDATE') THEN
            NEW.last_changes = now();  
            IF (OLD.executor != NEW.executor) THEN
                INSERT INTO "Tasks_audit" (operation, task_id, old_executor, new_executor, customer, who_notify_in_tg) 
                SELECT 'U_executor', OLD.id, OLD.executor, NEW.executor, NEW.customer, concat(OLD.executor, ' ', NEW.executor);
            ElSEIF (OLD.status != NEW.status) THEN
                INSERT INTO "Tasks_audit" (operation, task_id, old_status, new_status, customer, who_notify_in_tg) 
                SELECT 'U_status', OLD.id, OLD.status, NEW.status, NEW.customer, concat(OLD.executor);
            ElSEIF (OLD.dedline != NEW.dedline) THEN
                INSERT INTO "Tasks_audit" (operation, task_id, task_deadline, customer, who_notify_in_tg) 
                SELECT 'U_deadline', OLD.id,  NEW.dedline, NEW.customer, concat(OLD.executor);
            ElSEIF (OLD.header != NEW.header) THEN
                INSERT INTO "Tasks_audit" (operation, task_id, task_header, who_notify_in_tg) 
                SELECT 'U_header', OLD.id,  NEW.header, concat(OLD.executor);
            ElSEIF (OLD.mentor != NEW.mentor) THEN
                INSERT INTO "Tasks_audit" (operation, task_id, mentor, who_notify_in_tg) 
                SELECT 'U_mentor', OLD.id,  NEW.mentor, concat(OLD.executor, ' ',OLD.mentor, ' ',NEW.mentor);
             ElSEIF (OLD.task != NEW.task) THEN
                INSERT INTO "Tasks_audit" (operation, task_id, task_body, who_notify_in_tg)
                SELECT 'U_body', OLD.id,  OLD.task, concat(OLD.executor, ' ', OLD.customer);
            ELSE 
                INSERT INTO "Tasks_audit" (operation, task_id, who_notify_in_tg) 
                SELECT 'U', OLD.id, concat(OLD.executor);
            END IF;
        END IF;

        RETURN NEW;
    END;
$Tasks_audit$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS "Tasks_audit" on "Tasks";
CREATE TRIGGER "Tasks_audit"
AFTER INSERT OR UPDATE OR DELETE ON "Tasks"
    FOR EACH ROW EXECUTE FUNCTION "process_Tasks_audit"();