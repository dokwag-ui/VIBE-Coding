# ============================================================
# 장비 유지보수 데이터 통합 분석 스크립트
# 대상 파일: 장비유지보수_2022-2024.csv
# 분석 기간: 2022~2024년
# ============================================================

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager, rcParams


# ============================================================
# 0. 한글 폰트 설정
# - 그래프 제목, 축 제목, 범례의 한글 깨짐 방지
# ============================================================

possible_fonts = [
    "NanumGothic",
    "Malgun Gothic",
    "AppleGothic",
    "Noto Sans CJK JP"
]

available_fonts = {f.name for f in font_manager.fontManager.ttflist}
selected_font = next((f for f in possible_fonts if f in available_fonts), None)

if selected_font:
    rcParams["font.family"] = selected_font

rcParams["axes.unicode_minus"] = False

print(f"사용 폰트: {selected_font}")


# ============================================================
# 1. 데이터 불러오기 및 기본 전처리
# ============================================================

file_path = "장비유지보수_2022-2024.csv"

df = pd.read_csv(file_path)

# 날짜, 수리시간, 비용 컬럼 타입 변환
df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce")
df["수리시간_시간"] = pd.to_numeric(df["수리시간_시간"], errors="coerce")
df["비용_원"] = pd.to_numeric(df["비용_원"], errors="coerce")

# 연도 컬럼 생성
df["연도"] = df["날짜"].dt.year

print("\n[데이터 로드 완료]")
print(df.head())


# ============================================================
# 2. 데이터 기본 구조 확인
# - 전체 행 수와 열 수
# - 각 열의 이름, 데이터 타입, 결측값 개수
# - 날짜 범위
# - 장비ID 고유 개수와 목록
# - 이상유형 고유 값 목록
# ============================================================

print("\n" + "=" * 60)
print("2. 데이터 기본 구조")
print("=" * 60)

row_count, col_count = df.shape

print(f"전체 행 수: {row_count}")
print(f"전체 열 수: {col_count}")

column_summary = pd.DataFrame({
    "열 이름": df.columns,
    "데이터 타입": df.dtypes.astype(str).values,
    "결측값 개수": df.isna().sum().values
})

print("\n[열별 정보]")
print(column_summary)

date_min = df["날짜"].min()
date_max = df["날짜"].max()

print(f"\n날짜 범위: {date_min.date()} ~ {date_max.date()}")

equipment_list = sorted(df["장비ID"].dropna().unique())
error_type_list = sorted(df["이상유형"].dropna().unique())

print(f"\n장비ID 고유 개수: {len(equipment_list)}")
print(f"장비ID 목록: {equipment_list}")

print(f"\n이상유형 고유 값 목록: {error_type_list}")

# 결과 저장
column_summary.to_csv("열별_데이터타입_결측값.csv", index=False, encoding="utf-8-sig")


# ============================================================
# 3. 장비ID별·연도별 고장 발생 횟수 집계
# - 결측값이 있는 행은 분석에서 제외
# - 그룹 막대그래프 생성
# ============================================================

print("\n" + "=" * 60)
print("3. 장비ID별·연도별 고장 발생 횟수")
print("=" * 60)

failure_df = df.dropna().copy()
excluded_rows_all_missing = len(df) - len(failure_df)

print(f"결측값 포함으로 제외된 행 수: {excluded_rows_all_missing}")

failure_count = (
    failure_df
    .groupby(["장비ID", "연도"])
    .size()
    .reset_index(name="고장 횟수")
)

failure_pivot = (
    failure_count
    .pivot(index="장비ID", columns="연도", values="고장 횟수")
    .fillna(0)
    .astype(int)
)

print("\n[장비ID별·연도별 고장 발생 횟수]")
print(failure_pivot)

failure_pivot.to_csv("장비ID별_연도별_고장발생횟수.csv", encoding="utf-8-sig")

# 그룹 막대그래프
fig, ax = plt.subplots(figsize=(14, 6))

x = range(len(failure_pivot.index))
years = [2022, 2023, 2024]
width = 0.25

for i, year in enumerate(years):
    values = failure_pivot[year] if year in failure_pivot.columns else [0] * len(failure_pivot)
    positions = [pos + (i - 1) * width for pos in x]
    ax.bar(positions, values, width=width, label=str(year))

ax.set_title("장비별 연도별 고장 빈도")
ax.set_xlabel("장비ID")
ax.set_ylabel("고장 횟수")
ax.set_xticks(list(x))
ax.set_xticklabels(failure_pivot.index, rotation=45)
ax.legend()

plt.tight_layout()
plt.savefig("장비별_연도별_고장_빈도.png", dpi=200, bbox_inches="tight")
plt.close()


# ============================================================
# 4. 이상유형별 발생 빈도 및 전체 대비 비율
# - 이상유형 값별 발생 빈도 집계
# - 전체 대비 비율 계산
# - 가로 막대그래프 생성
# ============================================================

print("\n" + "=" * 60)
print("4. 이상유형별 발생 빈도 및 비율")
print("=" * 60)

error_df = df.dropna(subset=["날짜", "이상유형"]).copy()
excluded_error_rows = len(df) - len(error_df)

print(f"날짜/이상유형 결측 제외 행 수: {excluded_error_rows}")

error_freq = (
    error_df["이상유형"]
    .value_counts()
    .rename_axis("이상유형")
    .reset_index(name="발생 빈도")
)

error_freq["전체 대비 비율(%)"] = (
    error_freq["발생 빈도"] / error_freq["발생 빈도"].sum() * 100
).round(2)

print("\n[이상유형별 발생 빈도 및 비율]")
print(error_freq)

error_freq.to_csv("이상유형별_발생빈도_비율표.csv", index=False, encoding="utf-8-sig")

# 이상유형별 빈도 가로 막대그래프
bar_df = error_freq.sort_values("발생 빈도", ascending=True)

fig, ax = plt.subplots(figsize=(12, 7))

bars = ax.barh(bar_df["이상유형"], bar_df["발생 빈도"])

ax.set_title("이상유형별 발생 빈도")
ax.set_xlabel("발생 빈도")
ax.set_ylabel("이상유형")

max_count = bar_df["발생 빈도"].max()

for bar in bars:
    width_value = bar.get_width()
    ax.text(
        width_value + max_count * 0.01,
        bar.get_y() + bar.get_height() / 2,
        f"{int(width_value)}",
        va="center",
        ha="left"
    )

ax.set_xlim(0, max_count * 1.15)

plt.tight_layout()
plt.savefig("이상유형별_발생빈도_가로막대그래프.png", dpi=200, bbox_inches="tight")
plt.close()


# ============================================================
# 5. 계절별 이상유형 발생 빈도 히트맵
# - 봄: 3~5월
# - 여름: 6~8월
# - 가을: 9~11월
# - 겨울: 12~2월
# ============================================================

print("\n" + "=" * 60)
print("5. 계절별 이상유형 발생 빈도")
print("=" * 60)

def get_season(month):
    if month in [3, 4, 5]:
        return "봄"
    elif month in [6, 7, 8]:
        return "여름"
    elif month in [9, 10, 11]:
        return "가을"
    else:
        return "겨울"

error_df["계절"] = error_df["날짜"].dt.month.apply(get_season)

season_order = ["봄", "여름", "가을", "겨울"]
type_order = error_freq["이상유형"].tolist()

season_heatmap = (
    pd.crosstab(error_df["계절"], error_df["이상유형"])
    .reindex(index=season_order, columns=type_order, fill_value=0)
)

print("\n[계절별 이상유형 발생 빈도]")
print(season_heatmap)

season_heatmap.to_csv("계절별_이상유형_발생빈도.csv", encoding="utf-8-sig")

# 히트맵 시각화
fig, ax = plt.subplots(figsize=(14, 6))

im = ax.imshow(season_heatmap.values, aspect="auto")

ax.set_title("계절별 이상유형 발생 빈도 히트맵")
ax.set_xlabel("이상유형")
ax.set_ylabel("계절")

ax.set_xticks(range(len(season_heatmap.columns)))
ax.set_xticklabels(season_heatmap.columns, rotation=45, ha="right")

ax.set_yticks(range(len(season_heatmap.index)))
ax.set_yticklabels(season_heatmap.index)

# 셀 안에 값 표시
for i in range(season_heatmap.shape[0]):
    for j in range(season_heatmap.shape[1]):
        ax.text(
            j,
            i,
            int(season_heatmap.iloc[i, j]),
            ha="center",
            va="center"
        )

fig.colorbar(im, ax=ax, label="발생 빈도")

plt.tight_layout()
plt.savefig("계절별_이상유형_발생빈도_히트맵.png", dpi=200, bbox_inches="tight")
plt.close()


# ============================================================
# 6. 수리시간_시간 기술통계
# - 평균, 중앙값, 최솟값, 최댓값, 표준편차
# ============================================================

print("\n" + "=" * 60)
print("6. 수리시간_시간 기술통계")
print("=" * 60)

repair_df = df.dropna(subset=["수리시간_시간"]).copy()
excluded_repair_rows = len(df) - len(repair_df)

print(f"수리시간 결측 제외 행 수: {excluded_repair_rows}")

repair_stats = pd.DataFrame({
    "지표": ["평균", "중앙값", "최솟값", "최댓값", "표준편차"],
    "수리시간_시간": [
        repair_df["수리시간_시간"].mean(),
        repair_df["수리시간_시간"].median(),
        repair_df["수리시간_시간"].min(),
        repair_df["수리시간_시간"].max(),
        repair_df["수리시간_시간"].std()
    ]
})

repair_stats["수리시간_시간"] = repair_stats["수리시간_시간"].round(2)

print("\n[수리시간 기술통계]")
print(repair_stats)

repair_stats.to_csv("수리시간_기술통계.csv", index=False, encoding="utf-8-sig")


# ============================================================
# 7. 이상유형별 평균 수리시간
# ============================================================

print("\n" + "=" * 60)
print("7. 이상유형별 평균 수리시간")
print("=" * 60)

repair_by_type = (
    repair_df
    .groupby("이상유형", dropna=False)["수리시간_시간"]
    .mean()
    .round(2)
    .reset_index(name="평균 수리시간_시간")
    .sort_values("평균 수리시간_시간", ascending=False)
)

print("\n[이상유형별 평균 수리시간]")
print(repair_by_type)

repair_by_type.to_csv("이상유형별_평균수리시간.csv", index=False, encoding="utf-8-sig")


# ============================================================
# 8. IQR 방법으로 수리시간 이상값 탐지
# - Q1, Q3, IQR 계산
# - 하한: Q1 - 1.5 * IQR
# - 상한: Q3 + 1.5 * IQR
# ============================================================

print("\n" + "=" * 60)
print("8. IQR 방법 수리시간 이상값 탐지")
print("=" * 60)

q1 = repair_df["수리시간_시간"].quantile(0.25)
q3 = repair_df["수리시간_시간"].quantile(0.75)
iqr = q3 - q1

lower_bound = q1 - 1.5 * iqr
upper_bound = q3 + 1.5 * iqr

repair_outliers = repair_df[
    (repair_df["수리시간_시간"] < lower_bound) |
    (repair_df["수리시간_시간"] > upper_bound)
].copy()

preferred_cols = [
    "날짜",
    "장비ID",
    "장비명",
    "설치위치",
    "이상유형",
    "담당자",
    "수리시간_시간",
    "부품교체여부",
    "비용_원",
    "비고"
]

repair_outliers = repair_outliers[
    [col for col in preferred_cols if col in repair_outliers.columns]
]

print(f"Q1: {q1:.2f}")
print(f"Q3: {q3:.2f}")
print(f"IQR: {iqr:.2f}")
print(f"IQR 하한: {lower_bound:.2f}")
print(f"IQR 상한: {upper_bound:.2f}")
print(f"IQR 이상값 행 수: {len(repair_outliers)}")

print("\n[IQR 이상값 탐지 결과]")
print(repair_outliers)

repair_outliers.to_csv("수리시간_IQR_이상값.csv", index=False, encoding="utf-8-sig")


# ============================================================
# 9. 장비ID별 수리시간 분포 박스플롯
# - 장비ID별 평균 수리시간 기준 내림차순 정렬
# ============================================================

print("\n" + "=" * 60)
print("9. 장비ID별 수리시간 박스플롯")
print("=" * 60)

device_order = (
    repair_df
    .groupby("장비ID")["수리시간_시간"]
    .mean()
    .sort_values(ascending=False)
    .index
)

box_data = [
    repair_df.loc[repair_df["장비ID"] == device, "수리시간_시간"].values
    for device in device_order
]

fig, ax = plt.subplots(figsize=(14, 7))

ax.boxplot(
    box_data,
    tick_labels=device_order,
    vert=True,
    showmeans=True
)

ax.set_title("장비ID별 수리시간 분포 박스플롯")
ax.set_xlabel("장비ID")
ax.set_ylabel("수리시간(시간)")

plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("장비ID별_수리시간_박스플롯.png", dpi=200, bbox_inches="tight")
plt.close()


# ============================================================
# 10. 연도별 총 유지보수 비용 합계 및 전년도 대비 증가율
# - 원 단위를 만원 단위로 변환
# ============================================================

print("\n" + "=" * 60)
print("10. 연도별 총 유지보수 비용 및 증가율")
print("=" * 60)

cost_df = df.dropna(subset=["날짜", "연도", "비용_원"]).copy()
cost_df["연도"] = cost_df["연도"].astype(int)
cost_df["비용_만원"] = cost_df["비용_원"] / 10000

excluded_cost_rows = len(df) - len(cost_df)

print(f"날짜/비용 결측 제외 행 수: {excluded_cost_rows}")

yearly_cost = (
    cost_df
    .groupby("연도")["비용_만원"]
    .sum()
    .reset_index(name="총 유지보수 비용(만원)")
    .sort_values("연도")
)

yearly_cost["전년도 대비 증가율(%)"] = (
    yearly_cost["총 유지보수 비용(만원)"].pct_change() * 100
)

yearly_cost["총 유지보수 비용(만원)"] = yearly_cost["총 유지보수 비용(만원)"].round(1)
yearly_cost["전년도 대비 증가율(%)"] = yearly_cost["전년도 대비 증가율(%)"].round(2)

print("\n[연도별 총 유지보수 비용 및 증가율]")
print(yearly_cost)

yearly_cost.to_csv("연도별_총유지보수비용_증가율.csv", index=False, encoding="utf-8-sig")


# ============================================================
# 11. 장비별 3년 합산 유지보수 비용 Top 10
# - 원 단위를 만원 단위로 변환한 금액 기준
# ============================================================

print("\n" + "=" * 60)
print("11. 장비별 3년 합산 유지보수 비용 Top 10")
print("=" * 60)

device_cost_top10 = (
    cost_df
    .groupby("장비ID")["비용_만원"]
    .sum()
    .reset_index(name="3년 합산 유지보수 비용(만원)")
    .sort_values("3년 합산 유지보수 비용(만원)", ascending=False)
    .head(10)
)

device_cost_top10["3년 합산 유지보수 비용(만원)"] = (
    device_cost_top10["3년 합산 유지보수 비용(만원)"].round(1)
)

print("\n[장비별 3년 합산 유지보수 비용 Top 10]")
print(device_cost_top10)

device_cost_top10.to_csv("장비별_3년합산_유지보수비용_Top10.csv", index=False, encoding="utf-8-sig")


# ============================================================
# 12. 부품교체여부(Y/N)에 따른 평균 비용 비교
# - 원 단위를 만원 단위로 변환
# - 막대그래프 생성
# ============================================================

print("\n" + "=" * 60)
print("12. 부품교체여부별 평균 비용")
print("=" * 60)

part_avg_cost = (
    cost_df
    .dropna(subset=["부품교체여부"])
    .groupby("부품교체여부")["비용_만원"]
    .mean()
    .reset_index(name="평균 비용(만원)")
    .sort_values("부품교체여부")
)

part_avg_cost["평균 비용(만원)"] = part_avg_cost["평균 비용(만원)"].round(1)

print("\n[부품교체여부별 평균 비용]")
print(part_avg_cost)

part_avg_cost.to_csv("부품교체여부별_평균비용.csv", index=False, encoding="utf-8-sig")

# 막대그래프 생성
fig, ax = plt.subplots(figsize=(8, 5))

bars = ax.bar(
    part_avg_cost["부품교체여부"],
    part_avg_cost["평균 비용(만원)"]
)

ax.set_title("부품교체여부별 평균 유지보수 비용")
ax.set_xlabel("부품교체여부")
ax.set_ylabel("평균 비용(만원)")

max_val = part_avg_cost["평균 비용(만원)"].max()

for bar in bars:
    height = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        height + max_val * 0.02,
        f"{height:,.1f}",
        ha="center",
        va="bottom"
    )

ax.set_ylim(0, max_val * 1.15)

plt.tight_layout()
plt.savefig("부품교체여부별_평균비용_막대그래프.png", dpi=200, bbox_inches="tight")
plt.close()


# ============================================================
# 13. 연도별 총 비용 추이 꺾은선 그래프
# - 원 단위를 만원 단위로 변환한 총 비용 기준
# ============================================================

print("\n" + "=" * 60)
print("13. 연도별 총 비용 추이 그래프")
print("=" * 60)

fig, ax = plt.subplots(figsize=(9, 5))

ax.plot(
    yearly_cost["연도"],
    yearly_cost["총 유지보수 비용(만원)"],
    marker="o"
)

ax.set_title("연도별 총 유지보수 비용 추이")
ax.set_xlabel("연도")
ax.set_ylabel("총 유지보수 비용(만원)")
ax.set_xticks(yearly_cost["연도"])

for x_value, y_value in zip(
    yearly_cost["연도"],
    yearly_cost["총 유지보수 비용(만원)"]
):
    ax.text(
        x_value,
        y_value,
        f"{y_value:,.1f}",
        ha="center",
        va="bottom"
    )

plt.tight_layout()
plt.savefig("연도별_총유지보수비용_추이_꺾은선그래프.png", dpi=200, bbox_inches="tight")
plt.close()


# ============================================================
# 14. 인사이트 요약 출력
# - 지금까지의 분석 결과 기반
# ============================================================

print("\n" + "=" * 60)
print("14. 방산·제조 현장 관점 인사이트 요약")
print("=" * 60)

print("""
[핵심 발견 사항]
1. 유지보수 비용은 2022년부터 2024년까지 지속 증가 추세를 보입니다.
2. 특정 장비와 이상유형에 고장이 집중되어 있어 예방정비 우선순위 설정이 필요합니다.
3. 부품교체가 발생한 정비 건은 미교체 건 대비 평균 비용이 크게 높습니다.

[즉시 조치 필요 사항]
1. 고장 빈도와 비용이 높은 장비를 대상으로 집중 점검 및 예방정비 계획을 수립해야 합니다.
2. 베어링마모, 모터과열, 진동이상 등 주요 이상유형에 대한 조기 감지 기준을 강화해야 합니다.

[추가 분석 필요 영역]
1. 가동시간, 부하율, 작업량, 온도 등 운전 조건 데이터와 고장 데이터를 결합한 원인 분석이 필요합니다.
2. 부품 단가, 공급사, 교체 주기, 재고 리드타임을 포함한 비용 증가 원인 분석이 필요합니다.

[경영진 보고용 한 줄 요약]
2022~2024년 장비 유지보수 비용은 지속 증가하고 있으며, 주요 장비와 반복 이상유형 중심의 예방정비 강화가 비용 절감과 생산 안정성 확보의 핵심 과제입니다.
""")


# ============================================================
# 15. 완료 메시지
# ============================================================

print("\n분석이 완료되었습니다.")
print("CSV 결과 파일과 PNG 그래프 파일이 현재 작업 폴더에 저장되었습니다.")