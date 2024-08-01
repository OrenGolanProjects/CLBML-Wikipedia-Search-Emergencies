from services.peaks_service import PeaksService

def reset_paeks(app):
    print(">> START:: reset_paeks")
    PeaksService().peaks_check_and_create_figure_directory()
    print(">> END:: reset_paeks")
