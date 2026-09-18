import pytest
from app.utils.arabic_nlp import (
    normalize_arabic, extract_egx_ticker,
    determine_sentiment_lean, is_macro_or_market_subject
)

def test_arabic_normalization():
    assert normalize_arabic("أحمد إبراهيم آسر") == "احمد ابراهيم اسر"
    assert normalize_arabic("الشركة القابضة") == "الشركه القابضه"
    assert normalize_arabic("البَوْرَصَةُ المِصْرِيَّةُ") == "البورصه المصريه"
    assert normalize_arabic("مــصــر") == "مصر"

def test_egx_ticker_extraction():
    assert extract_egx_ticker("سهم البنك التجاري الدولي يسجل مكاسب") == "COMI.CA"
    assert extract_egx_ticker("ارتفاع أرباح فوري للمدفوعات الالكترونية") == "FWRY.CA"
    assert extract_egx_ticker("صفقة ضخمة لمجموعة طلعت مصطفى في رأس الحكمة") == "TMGH.CA"
    assert extract_egx_ticker("Elsewedy Electric announces new contract") == "SWDY.CA"
    assert extract_egx_ticker("COMI reaches all-time high on EGX") == "COMI.CA"

def test_sentiment_lean_detection():
    assert determine_sentiment_lean("قفزة قياسية في أرباح الشركة للربع الثالث") == 1
    assert determine_sentiment_lean("خسائر فادحة وهبوط حاد في صافي الدخل") == -1
    assert determine_sentiment_lean("اجتماع الجمعية العمومية للشركة") == 0

def test_macro_subject_gate():
    assert is_macro_or_market_subject("البنك المركزي المصري يرفع أسعار الفائدة") is True
    assert is_macro_or_market_subject("تقرير التضخم الصادر عن جهاز التعبئة والإحصاء") is True
    assert is_macro_or_market_subject("أخبار الدوري المصري لكرة القدم") is False
