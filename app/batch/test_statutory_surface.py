from app.services.legal_checks import detect_statutory_surface_right

sample = """
본 건은 법정지상권 성립 여부 검토 대상임.
"""

result = detect_statutory_surface_right(sample)

print(result)
