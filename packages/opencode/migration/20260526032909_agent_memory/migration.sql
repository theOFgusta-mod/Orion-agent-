CREATE TABLE `agent_memory` (
	`id` integer PRIMARY KEY AUTOINCREMENT,
	`key` text NOT NULL,
	`value` text NOT NULL,
	`scope` text DEFAULT 'global' NOT NULL,
	`agent_id` text DEFAULT 'orion' NOT NULL,
	`category` text DEFAULT 'general',
	`time_created` integer NOT NULL,
	`time_updated` integer NOT NULL
);
--> statement-breakpoint
CREATE INDEX `memory_key_idx` ON `agent_memory` (`key`);--> statement-breakpoint
CREATE INDEX `memory_scope_idx` ON `agent_memory` (`scope`);--> statement-breakpoint
CREATE INDEX `memory_agent_idx` ON `agent_memory` (`agent_id`);--> statement-breakpoint
CREATE INDEX `memory_category_idx` ON `agent_memory` (`category`);