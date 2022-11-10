export interface BlogPosts {
  posts: BlogPost[];
}

export interface BlogPost {
  id: number;
  title: string;
  slug: string;
  author: {
    first_name: string;
    last_name: string;
    email: string;
    username: string;
  };
  lead?: string;
  content: string;
  blurb: string;
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
  created: string;
  updated: string;
  published: boolean;
  order: number;
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
