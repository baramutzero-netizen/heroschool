"""Refuse to publish an accidentally restored legacy battle renderer."""
def validate_game_source(source):
    required = {
        '256px 프레임': 'const SPR_CELL=256,',
        '프레임 좌표': 'SPR_META=',
        '70% 재생 속도': 'const SPR_PLAYBACK_RATE = 0.7;',
        '대각선 전투 필드': 'class="bf-stage"',
        '성격별 대사': 'function battleCallout(',
        '효과 아이콘': 'function battleStatusIcon(',
        '직업별 필살기': 'function ultimateEffect(',
        '보호막 표시': 'class="bf-shield"',
        '의식 상태 색상': '.bf-meter.hp.stupor',
    }
    missing = [name for name, marker in required.items() if marker not in source]
    if missing:
        raise RuntimeError('Build stopped: game.html appears to contain a legacy battle renderer. '
                           'Restore/merge the current source before rebuilding. Missing: '
                           + ', '.join(missing))
