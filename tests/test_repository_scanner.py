"""
Tests for Repository Scanner functionality.

Tests the scan_local_repo.py script and RepositoryScanner class for multi-language
code analysis (Python, JavaScript, TypeScript, Java, C++, Go, etc.).
"""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scan_local_repo import RepositoryScanner
from backend.models import SkillTag


class TestRepositoryScanner:
    """Test suite for RepositoryScanner class."""
    
    @pytest.fixture
    def mock_db_connection(self):
        """Mock MongoDB connection string."""
        return "mongodb://localhost:27017/test_db"
    
    @pytest.fixture
    def mock_api_key(self):
        """Mock Gemini API key."""
        return "test_api_key_12345"
    
    @pytest.fixture
    def temp_directory(self):
        """Create temporary directory with code files in multiple languages."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create Python file
            test_file_1 = Path(tmpdir) / "test_module.py"
            test_file_1.write_text("""
import fastapi
from pydantic import BaseModel

class User(BaseModel):
    name: str
    email: str
""")
            
            # Create JavaScript file
            test_file_2 = Path(tmpdir) / "app.js"
            test_file_2.write_text("""
const express = require('express');
const mongoose = require('mongoose');

const app = express();
app.listen(3000);
""")
            
            # Create TypeScript file
            test_file_3 = Path(tmpdir) / "utils.ts"
            test_file_3.write_text("""
import React from 'react';
import axios from 'axios';

export const fetchData = async () => {
    return await axios.get('/api/data');
};
""")
            
            # Create ignored directory
            ignored_dir = Path(tmpdir) / "__pycache__"
            ignored_dir.mkdir()
            (ignored_dir / "cached.py").write_text("# Should be ignored")
            
            yield tmpdir
    
    def test_scanner_initialization(self, mock_db_connection, mock_api_key):
        """Test that scanner initializes correctly."""
        with patch('scan_local_repo.SkillEngine') as mock_skill_engine, \
             patch('scan_local_repo.pymongo.MongoClient') as mock_mongo:
            
            # Mock MongoDB connection
            mock_client = Mock()
            mock_db = Mock()
            mock_client.__getitem__ = Mock(return_value=mock_db)
            mock_client.admin.command.return_value = {"ok": 1}
            mock_mongo.return_value = mock_client
            
            scanner = RepositoryScanner(mock_db_connection, mock_api_key)
            
            assert scanner is not None
            mock_skill_engine.assert_called_once_with(api_key=mock_api_key)
            mock_mongo.assert_called_once()
    
    def test_scan_directory_finds_python_files(self, temp_directory, mock_db_connection, mock_api_key):
        """Test that scanner finds code files in multiple languages and ignores excluded directories."""
        with patch('scan_local_repo.SkillEngine'), \
             patch('scan_local_repo.pymongo.MongoClient') as mock_mongo:
            
            # Mock MongoDB connection
            mock_client = Mock()
            mock_db = Mock()
            mock_client.__getitem__ = Mock(return_value=mock_db)
            mock_client.admin.command.return_value = {"ok": 1}
            mock_mongo.return_value = mock_client
            
            scanner = RepositoryScanner(mock_db_connection, mock_api_key)
            
            # Scan directory
            files = scanner.scan_directory(temp_directory)
            
            # Should find 3 code files (test_module.py, app.js, utils.ts)
            assert len(files) == 3
            
            # Should not include files from __pycache__
            assert not any("__pycache__" in f for f in files)
            
            # Verify file names
            file_names = [Path(f).name for f in files]
            assert "test_module.py" in file_names
            assert "app.js" in file_names
            assert "utils.ts" in file_names
    
    def test_scan_directory_nonexistent_path(self, mock_db_connection, mock_api_key):
        """Test that scanner raises error for nonexistent directory."""
        with patch('scan_local_repo.SkillEngine'), \
             patch('scan_local_repo.pymongo.MongoClient') as mock_mongo:
            
            # Mock MongoDB connection
            mock_client = Mock()
            mock_db = Mock()
            mock_client.__getitem__ = Mock(return_value=mock_db)
            mock_client.admin.command.return_value = {"ok": 1}
            mock_mongo.return_value = mock_client
            
            scanner = RepositoryScanner(mock_db_connection, mock_api_key)
            
            with pytest.raises(FileNotFoundError):
                scanner.scan_directory("/nonexistent/path")
    
    def test_scan_directory_empty_directory(self, mock_db_connection, mock_api_key):
        """Test that scanner handles empty directory gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir, \
             patch('scan_local_repo.SkillEngine'), \
             patch('scan_local_repo.pymongo.MongoClient') as mock_mongo:
            
            # Mock MongoDB connection
            mock_client = Mock()
            mock_db = Mock()
            mock_client.__getitem__ = Mock(return_value=mock_db)
            mock_client.admin.command.return_value = {"ok": 1}
            mock_mongo.return_value = mock_client
            
            scanner = RepositoryScanner(mock_db_connection, mock_api_key)
            
            # Scan empty directory
            files = scanner.scan_directory(tmpdir)
            
            # Should return empty list
            assert len(files) == 0
    
    @pytest.mark.asyncio
    async def test_extract_skills_from_files(self, temp_directory, mock_db_connection, mock_api_key):
        """Test skill extraction from files."""
        with patch('scan_local_repo.SkillEngine') as mock_skill_engine_class, \
             patch('scan_local_repo.pymongo.MongoClient') as mock_mongo:
            
            # Mock MongoDB connection
            mock_client = Mock()
            mock_db = Mock()
            mock_client.__getitem__ = Mock(return_value=mock_db)
            mock_client.admin.command.return_value = {"ok": 1}
            mock_mongo.return_value = mock_client
            
            # Mock SkillEngine
            mock_skill_engine = Mock()
            mock_skill_engine.analyze_code_file = AsyncMock(return_value="FastAPI, Pydantic, NumPy")
            mock_skill_engine_class.return_value = mock_skill_engine
            
            scanner = RepositoryScanner(mock_db_connection, mock_api_key)
            
            # Get files
            files = scanner.scan_directory(temp_directory)
            
            # Extract skills
            skills = await scanner.extract_skills_from_files(files)
            
            # Should extract skills
            assert len(skills) > 0
            
            # Verify skills are SkillTag objects
            assert all(isinstance(skill, SkillTag) for skill in skills)
            
            # Verify skill names
            skill_names = [skill.name for skill in skills]
            assert "FastAPI" in skill_names or "Pydantic" in skill_names or "NumPy" in skill_names
    
    @pytest.mark.asyncio
    async def test_aggregate_skills_summary(self, mock_db_connection, mock_api_key):
        """Test skill aggregation into summary string."""
        with patch('scan_local_repo.SkillEngine'), \
             patch('scan_local_repo.pymongo.MongoClient') as mock_mongo:
            
            # Mock MongoDB connection
            mock_client = Mock()
            mock_db = Mock()
            mock_client.__getitem__ = Mock(return_value=mock_db)
            mock_client.admin.command.return_value = {"ok": 1}
            mock_mongo.return_value = mock_client
            
            scanner = RepositoryScanner(mock_db_connection, mock_api_key)
            
            # Create test skills
            skills = [
                SkillTag(name="FastAPI", confidence=0.9, evidence_file="main.py"),
                SkillTag(name="MongoDB", confidence=0.85, evidence_file="database.py"),
                SkillTag(name="Pydantic", confidence=0.95, evidence_file="models.py")
            ]
            
            # Aggregate skills
            summary = await scanner.aggregate_skills_summary(skills)
            
            # Verify summary contains skill names
            assert "FastAPI" in summary
            assert "MongoDB" in summary
            assert "Pydantic" in summary
    
    @pytest.mark.asyncio
    async def test_generate_master_embedding(self, mock_db_connection, mock_api_key):
        """Test master embedding generation."""
        with patch('scan_local_repo.SkillEngine') as mock_skill_engine_class, \
             patch('scan_local_repo.pymongo.MongoClient') as mock_mongo:
            
            # Mock MongoDB connection
            mock_client = Mock()
            mock_db = Mock()
            mock_client.__getitem__ = Mock(return_value=mock_db)
            mock_client.admin.command.return_value = {"ok": 1}
            mock_mongo.return_value = mock_client
            
            # Mock SkillEngine with embedding
            mock_skill_engine = Mock()
            mock_embedding = [0.1] * 768  # 768-dimensional vector
            mock_skill_engine.create_embedding = AsyncMock(return_value=mock_embedding)
            mock_skill_engine_class.return_value = mock_skill_engine
            
            scanner = RepositoryScanner(mock_db_connection, mock_api_key)
            
            # Generate embedding
            embedding = await scanner.generate_master_embedding("FastAPI, MongoDB, Pydantic")
            
            # Verify embedding
            assert len(embedding) == 768
            assert all(isinstance(x, float) for x in embedding)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
