import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Tuple, Optional

class DouyinDatabase:
    def __init__(self, db_path: str = "douyin_links.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create main links table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS douyin_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL UNIQUE,
                title TEXT,
                author TEXT,
                content TEXT,
                notes TEXT,
                category TEXT DEFAULT '未分类',
                analysis TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_link(self, url: str, title: str = "", author: str = "", 
                 content: str = "", notes: str = "", category: str = "未分类") -> Tuple[bool, str]:
        """Add a new Douyin link"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO douyin_links (url, title, author, content, notes, category)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (url, title, author, content, notes, category))
            
            conn.commit()
            conn.close()
            return True, "链接已成功保存"
        except sqlite3.IntegrityError:
            return False, "链接已存在，跳过重复"
        except Exception as e:
            return False, f"保存失败: {str(e)}"
    
    def get_all_links(self) -> List[Dict]:
        """Get all links"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM douyin_links ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def search_links(self, keyword: str) -> List[Dict]:
        """Search links by keyword"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM douyin_links 
            WHERE url LIKE ? OR title LIKE ? OR author LIKE ? OR content LIKE ? OR notes LIKE ?
            ORDER BY created_at DESC
        ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_by_category(self, category: str) -> List[Dict]:
        """Get links by category"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM douyin_links WHERE category = ? ORDER BY created_at DESC', (category,))
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def update_link(self, link_id: int, title: str = None, author: str = None, 
                    content: str = None, notes: str = None, category: str = None, analysis: str = None) -> Tuple[bool, str]:
        """Update link information"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            updates = []
            params = []
            
            if title is not None:
                updates.append('title = ?')
                params.append(title)
            if author is not None:
                updates.append('author = ?')
                params.append(author)
            if content is not None:
                updates.append('content = ?')
                params.append(content)
            if notes is not None:
                updates.append('notes = ?')
                params.append(notes)
            if category is not None:
                updates.append('category = ?')
                params.append(category)
            if analysis is not None:
                updates.append('analysis = ?')
                params.append(analysis)
            
            if not updates:
                return False, "没有更新内容"
            
            updates.append('updated_at = CURRENT_TIMESTAMP')
            params.append(link_id)
            
            query = f'UPDATE douyin_links SET {', '.join(updates)} WHERE id = ?'
            cursor.execute(query, params)
            
            conn.commit()
            conn.close()
            return True, "更新成功"
        except Exception as e:
            return False, f"更新失败: {str(e)}"
    
    def delete_link(self, link_id: int) -> Tuple[bool, str]:
        """Delete a link"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM douyin_links WHERE id = ?', (link_id,))
            
            conn.commit()
            conn.close()
            return True, "删除成功"
        except Exception as e:
            return False, f"删除失败: {str(e)}"
    
    def get_categories(self) -> List[str]:
        """Get all unique categories"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT DISTINCT category FROM douyin_links ORDER BY category')
        rows = cursor.fetchall()
        conn.close()
        
        return [row[0] for row in rows]
    
    def export_to_csv(self, filepath: str) -> Tuple[bool, str]:
        """Export all links to CSV"""
        try:
            import pandas as pd
            links = self.get_all_links()
            
            if not links:
                return False, "没有数据可导出"
            
            df = pd.DataFrame(links)
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            return True, f"已导出到 {filepath}"
        except Exception as e:
            return False, f"导出失败: {str(e)}"
    
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM douyin_links')
        total = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM douyin_links WHERE analysis IS NOT NULL')
        analyzed = cursor.fetchone()[0]
        
        cursor.execute('SELECT category, COUNT(*) as count FROM douyin_links GROUP BY category')
        categories = cursor.fetchall()
        
        conn.close()
        
        return {
            'total': total,
            'analyzed': analyzed,
            'categories': {row[0]: row[1] for row in categories}
        }
