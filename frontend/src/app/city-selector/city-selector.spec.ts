import { ComponentFixture, TestBed } from '@angular/core/testing';
import { CitySelectorComponent } from './city-selector';

describe('CitySelectorComponent', () => {
  let component: CitySelectorComponent;
  let fixture: ComponentFixture<CitySelectorComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CitySelectorComponent]
    }).compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(CitySelectorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should render city options', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    const options = compiled.querySelectorAll('option');
    expect(options.length).toBe(component.cities.length + 1); // includes placeholder
  });
});
