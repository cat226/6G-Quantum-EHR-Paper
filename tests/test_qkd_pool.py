"""Unit tests for the QKD pool model (Task 8 Phase 16)."""

import pytest

from src.crypto.qkd import QKDInsufficientMaterial, QKDPool, QKDPoolConfig


def test_pool_starts_full_by_default():
    pool = QKDPool(QKDPoolConfig(capacity_bits=1000, generation_rate_bits_per_sec=100))
    assert pool.available_fraction() == pytest.approx(1.0)


def test_draw_reduces_level():
    pool = QKDPool(QKDPoolConfig(capacity_bits=1000, generation_rate_bits_per_sec=0))
    material = pool.draw(100)
    assert len(material) == 13  # ceil(100/8) bytes
    assert pool.level_bits == 900


def test_draw_insufficient_raises():
    pool = QKDPool(QKDPoolConfig(capacity_bits=100, generation_rate_bits_per_sec=0))
    with pytest.raises(QKDInsufficientMaterial):
        pool.draw(200)


def test_draw_does_not_fall_back_or_partially_succeed():
    """Task 8 Phase 6: 'do NOT automatically fall back inside the QKD
    module.' Confirms an insufficient draw raises cleanly rather than
    returning a partial/short result."""
    pool = QKDPool(QKDPoolConfig(capacity_bits=50, generation_rate_bits_per_sec=0))
    level_before = pool.level_bits
    with pytest.raises(QKDInsufficientMaterial):
        pool.draw(100)
    assert pool.level_bits == level_before  # untouched on failure


def test_tick_replenishes_up_to_capacity():
    pool = QKDPool(QKDPoolConfig(capacity_bits=1000, generation_rate_bits_per_sec=100, initial_fill_fraction=0.0))
    assert pool.level_bits == 0
    pool.tick(5.0)  # 5 seconds * 100 bits/sec = 500 bits
    assert pool.level_bits == pytest.approx(500)
    pool.tick(100.0)  # would overshoot capacity
    assert pool.level_bits == pytest.approx(1000)


def test_outage_prevents_replenishment():
    pool = QKDPool(QKDPoolConfig(capacity_bits=1000, generation_rate_bits_per_sec=100, initial_fill_fraction=0.5))
    pool.set_outage(True)
    pool.tick(10.0)
    assert pool.level_bits == pytest.approx(500)  # unchanged during outage


def test_outage_still_allows_draining():
    pool = QKDPool(QKDPoolConfig(capacity_bits=1000, generation_rate_bits_per_sec=100, initial_fill_fraction=1.0))
    pool.set_outage(True)
    pool.draw(200)
    assert pool.level_bits == pytest.approx(800)


def test_clearing_outage_resumes_generation():
    pool = QKDPool(QKDPoolConfig(capacity_bits=1000, generation_rate_bits_per_sec=100, initial_fill_fraction=0.0))
    pool.set_outage(True)
    pool.tick(5.0)
    assert pool.level_bits == 0
    pool.set_outage(False)
    pool.tick(5.0)
    assert pool.level_bits == pytest.approx(500)


def test_available_fraction_zero_capacity_does_not_divide_by_zero():
    pool = QKDPool(QKDPoolConfig(capacity_bits=0, generation_rate_bits_per_sec=0))
    assert pool.available_fraction() == 0.0
