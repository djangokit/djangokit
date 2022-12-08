export interface BlogPosts {
  posts: BlogPost[];
}

export interface BlogPost {
  id: number;
  title: string;
  slug: string;
  lead?: string;
  content: string;
  created: string;
  updated: string;
  published?: string;
}

export interface Page {
  id: number;
  title: string;
  slug: string;
  lead?: string;
  content: string;
}

export interface TodoItems {
  todo: TodoItem[];
  completed: TodoItem[];
}

export interface TodoItem {
  id: number;
  rawContent: string; // Markdown
  content: string; // HTML
  created: string;
  completed: string;
}
